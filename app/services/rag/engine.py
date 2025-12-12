from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.vector_stores.supabase import SupabaseVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.llms import CustomLLM, CompletionResponse, CompletionResponseGen, LLMMetadata
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings as LlamaSettings
from app.core.config import settings
from app.core.key_manager import key_manager
import google.generativeai as genai
import logging
import os
from typing import Any, Generator

logger = logging.getLogger(__name__)

class CustomGemini(CustomLLM):
    context_window: int = 32000
    num_output: int = 2048
    model_name: str = "models/gemini-flash-latest"
    api_key: str = None
    _model: Any = None

    def __init__(self, api_key: str, model_name: str = "models/gemini-flash-latest"):
        super().__init__()
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model_name)

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_name,
        )

    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        try:
            response = self._model.generate_content(prompt)
            return CompletionResponse(text=response.text)
        except Exception as e:
            logger.error(f"Gemini Generation Error: {e}")
            raise

    def stream_complete(self, prompt: str, **kwargs: Any) -> Generator[CompletionResponse, None, None]:
        response = self._model.generate_content(prompt, stream=True)
        text = ""
        for chunk in response:
            text += chunk.text
            yield CompletionResponse(text=text, delta=chunk.text)

class RAGService:
    def __init__(self):
        # 1. Setup Embeddings
        self.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        LlamaSettings.embed_model = self.embed_model
        
        # 2. Vector Store
        if settings.SUPABASE_DB_URL:
            logger.info("Connecting to Supabase Vector Store (Production Mode)...")
            self.vector_store = SupabaseVectorStore(
                postgres_connection_string=settings.SUPABASE_DB_URL, 
                collection_name="pdf_cortex_vectors",
                dimension=384
            )
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        elif settings.SUPABASE_URL and settings.SUPABASE_KEY:
             logger.warning("Supabase URL found but SUPABASE_DB_URL missing. Vector Store needs Postgres Connection String.")
             self.vector_store = None
             self.storage_context = None
        else:
            logger.info("Using Local Vector Store (Demo Mode)")
            self.vector_store = None
            self.storage_context = None

    def _get_llm(self):
        """
        Hydra Strategy: Rotate keys for every request from the Pool.
        Using CustomGemini Wrapper for reliability.
        """
        active_key = key_manager.get_next_key()
        # Using gemini-flash-latest confirmed by Quota Hunter
        return CustomGemini(
            model_name="models/gemini-flash-latest", 
            api_key=active_key
        )

    def index_document(self, text_dir: str, pdf_id: str):
        logger.info(f"Indexing document {pdf_id} from {text_dir}")
        
        def filename_to_metadata(filename: str):
            try:
                basename = os.path.basename(filename)
                page_str = basename.split("_")[1].split(".")[0]
                return {"page_number": int(page_str), "pdf_id": pdf_id}
            except:
                return {"pdf_id": pdf_id}

        documents = SimpleDirectoryReader(
            text_dir, 
            file_metadata=filename_to_metadata
        ).load_data()
        
        parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
        nodes = parser.get_nodes_from_documents(documents)
        
        if self.vector_store:
            index = VectorStoreIndex(
                nodes, 
                storage_context=self.storage_context
            )
        else:
            persist_dir = f"data/indices/{pdf_id}"
            if os.path.exists(persist_dir):
                pass 
                
            index = VectorStoreIndex(nodes)
            index.storage_context.persist(persist_dir=persist_dir)
            
        logger.info(f"Indexing complete for {pdf_id}")
        return index

    def query(self, query_text: str, pdf_id: str):
        # Load Index
        if self.vector_store:
            index = VectorStoreIndex.from_vector_store(
                self.vector_store,
                embed_model=self.embed_model
            )
        else:
            persist_dir = f"data/indices/{pdf_id}"
            if not os.path.exists(persist_dir):
                return "Error: Document not indexed."
                
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)
            
        # Custom Prompt for Spanish Interaction
        from llama_index.core import PromptTemplate
        
        qa_prompt_tmpl_str = (
            "Eres un asistente inteligente y útil experto en analizar libros y documentos educativos.\n"
            "INSTRUCCIONES PRINCIPALES:\n"
            "1. Para preguntas sobre el contenido del libro: Responde EXCLUSIVAMENTE basándote en el contexto proporcionado abajo.\n"
            "2. Para saludos (Hola, Buenos días) o preguntas personales (Cómo estás): Responde amablemente, profesionalmente y ofrece tu ayuda con el libro.\n"
            "3. Si la respuesta a una pregunta de contenido no está en el contexto: Dilo amablemente, no inventes información.\n"
            "4. Responde siempre en ESPAÑOL.\n"
            "---------------------\n"
            "Contexto:\n"
            "{context_str}\n"
            "---------------------\n"
            "Interacción del Usuario: {query_str}\n"
            "Respuesta:"
        )
        qa_prompt = PromptTemplate(qa_prompt_tmpl_str)

        # Create Engine with Dynamic Key Rotation
        try:
            current_llm = self._get_llm()
            query_engine = index.as_query_engine(
                similarity_top_k=10, 
                text_qa_template=qa_prompt,
                llm=current_llm
            )
            response = query_engine.query(query_text)
        except Exception as e:
            logger.error(f"LLM Query Failed: {e}")
            return {
                "answer": f"Lo siento, hubo un error técnico ({str(e)}). Intenta de nuevo.",
                "sources": []
            }
        
        # Extract Source Nodes
        sources = []
        for node in response.source_nodes:
            sources.append({
                "text": node.node.get_text()[:50] + "...",
                "page": node.node.metadata.get("page_number", "Unknown"),
                "score": node.score
            })
            
        return {
            "answer": str(response),
            "sources": sources
        }

    async def query_swarm(self, query_text: str, pdf_id: str):
        """
        SWARM MODE: Fires 3 simultaneous queries with different keys/perspectives.
        """
        import asyncio
        
        # 1. Get Context (Shared)
        if self.vector_store:
            index = VectorStoreIndex.from_vector_store(
                self.vector_store, embed_model=self.embed_model
            )
        else:
            persist_dir = f"data/indices/{pdf_id}"
            if not os.path.exists(persist_dir):
                 return {"answer": "Swarm Error: Doc not found.", "sources": []}
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)

        retriever = index.as_retriever(similarity_top_k=15) # Deep retrieval
        nodes = retriever.retrieve(query_text)
        
        # 2. Split Nodes for Agents (Sharding Strategy)
        # Agent 1 gets top 5, Agent 2 gets mid 5, Agent 3 gets mix
        chunk_1 = nodes[:5]
        chunk_2 = nodes[5:10]
        chunk_3 = nodes[10:15] if len(nodes) > 10 else nodes[:5]
        
        # 3. Define Async Worker
        async def run_agent(agent_id, context_nodes, key):
            # Lightweight instantiation
            llm = CustomGemini(model_name="models/gemini-flash-latest", api_key=key)
            
            "text": n.node.get_text()[:50] + "...", 
            "page": n.node.metadata.get("page_number", "Multiple"), 
            "score": n.score
        } for n in nodes[:5]]

        return {
            "answer": f"**[Hydra Swarm 🐝]**\n\n{str(final_response)}",
            "sources": sources
        }

rag_service = RAGService()

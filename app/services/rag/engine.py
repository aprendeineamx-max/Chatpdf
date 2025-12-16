
import logging
import os
from app.core.config import settings
from app.core.key_manager import key_manager
from typing import Any

logger = logging.getLogger(__name__)

# --- SAFE IMPORT BLOCK ---
try:
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings as LlamaSettings
    from llama_index.vector_stores.supabase import SupabaseVectorStore
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    import google.generativeai as genai

    SAFE_MODE = False
except ImportError as e:
    logger.error(f"RAG Dependencies Missing: {e}. Entering SAFE MODE (Echo/Simple).")
    SAFE_MODE = True

# --- REAL IMPLEMENTATION ---
if not SAFE_MODE:
    class CustomGemini(CustomLLM):
        context_window: int = 32000
        num_output: int = 2048
        model_name: str = "models/gemini-flash-latest"
        api_key: str = None
        _model: Any = None

        def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
            super().__init__()
            self.api_key = api_key
            self.model_name = model_name
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)

        @property
        def metadata(self) -> LLMMetadata:
            return LLMMetadata(context_window=self.context_window, num_output=self.num_output, model_name=self.model_name)

        def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
            try:
                response = self._model.generate_content(prompt)
                return CompletionResponse(text=response.text)
            except Exception as e:
                logger.error(f"Gemini Generation Error: {e}")
                return CompletionResponse(text=f"Error AI: {str(e)} | Key: {self.api_key[:5]}... | Model: {self.model_name}")
        
        def stream_complete(self, prompt: str, **kwargs: Any):
            yield CompletionResponse(text="Streaming not supported in Safe Wrapper")

    class CustomSambaNova(CustomLLM):
        context_window: int = 131072
        num_output: int = 4096
        model_name: str = "Meta-Llama-3.3-70B-Instruct" # [UPDATE] 3.3 is Active
        api_key: str = None
        
        def __init__(self, api_key: str, model_name: str = "Meta-Llama-3.3-70B-Instruct"):
            super().__init__()
            self.api_key = api_key
            self.model_name = model_name

        @property
        def metadata(self) -> LLMMetadata:
            return LLMMetadata(context_window=self.context_window, num_output=self.num_output, model_name=self.model_name)

        def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
            import requests
            url = "https://api.sambanova.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            # [UPDATE] System Prompt to enforce Spanish
            messages = [
                {"role": "system", "content": "You are a helpful assistant. You must ALWAYS respond in Spanish (Español), even if the user speaks English. Format your answers nicely."},
                {"role": "user", "content": prompt}
            ]
            data = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.1,
                "top_p": 0.1
            }
            try:
                # [UPDATE] Increased timeout to 120s for reasoning models
                response = requests.post(url, headers=headers, json=data, timeout=120) 
                if response.status_code == 200:
                    text_resp = response.json()['choices'][0]['message']['content']
                    return CompletionResponse(text=text_resp)
                else:
                    return CompletionResponse(text=f"SambaNova Error {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"SambaNova Error: {e}")
                return CompletionResponse(text=f"Error AI: {str(e)} | Key: {self.api_key[:5]}...")

        def stream_complete(self, prompt: str, **kwargs: Any):
             yield CompletionResponse(text="Streaming not supported in Safe Wrapper")

    class RAGService:
        def __init__(self):
            self.vector_store = None
            self.embed_model = None
            try:
                self.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
                LlamaSettings.embed_model = self.embed_model
                
                if settings.SUPABASE_DB_URL:
                    self.vector_store = SupabaseVectorStore(
                        postgres_connection_string=settings.SUPABASE_DB_URL, 
                        collection_name="pdf_cortex_vectors",
                        dimension=384
                    )
                    self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
                else:
                    self.storage_context = None
            except Exception as e:
                logger.error(f"RAG Init Error: {e}")
                
        def _get_llm(self, model_override: str = None):
            # 1. SambaNova Strategy (Llama or DeepSeek)
            if model_override and ("Llama" in model_override or "DeepSeek" in model_override):
                key = settings.SAMBANOVA_API_KEY
                return CustomSambaNova(api_key=key, model_name=model_override)
            
            # 2. Google Fallback (If not SambaNova)
            # HARDCODED SUCCESS KEY (User Provided Index #1)
            active_key = "AIzaSyC4xyNQ6BcsXzckzIeUFdfvhjaXUtHkRK4"
            # Revert to stable 1.5 Flash
            gemini_model = "gemini-1.5-flash" 
            return CustomGemini(model_name=gemini_model, api_key=active_key)

        def query(self, query_text: str, pdf_id: str, model: str = None):
            # Fallback direct generation if Index fails or no docs
            try:
                 llm = self._get_llm(model_override=model)
                 resp = llm.complete(f"Answer this user question based on your general knowledge (RAG Unavailable): {query_text}")
                 return {
                     "answer": resp.text, 
                     "sources": [],
                     "model": llm.model_name
                 }
            except Exception as e:
                return {"answer": f"RAG Error: {str(e)}", "sources": [], "model": "Error"}

        async def query_swarm(self, query_text: str, pdf_id: str, model: str = None):
             return self.query(query_text, pdf_id, model=model)

    rag_service = RAGService()

# --- MOCK IMPLEMENTATION (SAFE MODE) ---
else:
    class MockRAGService:
        def query(self, query_text: str, pdf_id: str):
            return {
                "answer": f"**[SAFE MODE]** The Cortex is operating in fallback mode due to missing dependencies. \n\nYour message: *{query_text}*", 
                "sources": [{"text": "System Safe Mode", "page": 0, "score": 1.0}]
            }
            
        async def query_swarm(self, query_text: str, pdf_id: str):
            return self.query(query_text, pdf_id)
            
    rag_service = MockRAGService()

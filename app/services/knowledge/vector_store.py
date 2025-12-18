"""
VectorStoreService - Semantic RAG with Embeddings

This service manages:
- Document chunking with overlap for context continuity
- Embedding generation using sentence-transformers
- Vector storage and retrieval using ChromaDB

Architecture:
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│ PDF Text    │ --> │ Chunk & Embed│ --> │ ChromaDB   │
└─────────────┘     └──────────────┘     └────────────┘
                           │                    │
                           v                    v
                    ┌──────────────┐     ┌────────────┐
                    │ Query Embed  │ --> │ Top-K Srch │
                    └──────────────┘     └────────────┘
"""

import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

# Lazy loading for heavy imports
_embedder = None
_splitter = None


def get_embedder():
    """Lazy load the embedding model to avoid slow startup."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model (first time only)...")
        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model loaded successfully.")
    return _embedder


def get_splitter():
    """Lazy load the text splitter."""
    global _splitter
    if _splitter is None:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        _splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,      # ~200 words per chunk
            chunk_overlap=200,    # Context continuity between chunks
            separators=["\n\n", "\n", ". ", ", ", " "],
            length_function=len
        )
    return _splitter


class VectorStoreService:
    """
    Service for semantic document storage and retrieval using embeddings.
    
    Uses ChromaDB for persistent vector storage and sentence-transformers
    for generating embeddings locally (no API calls needed).
    """
    
    def __init__(self, persist_dir: str = None):
        """Initialize the vector store with persistent storage."""
        if persist_dir is None:
            # Default to project data directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            persist_dir = os.path.join(base_dir, "data", "vector_store")
        
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(path=persist_dir)
        logger.info(f"VectorStore initialized at: {persist_dir}")
    
    def _sanitize_collection_name(self, name: str) -> str:
        """Sanitize collection name for ChromaDB requirements."""
        # ChromaDB requires: 3-63 chars, alphanumeric, underscores, hyphens
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        sanitized = sanitized[:60]  # Max 63 chars
        if len(sanitized) < 3:
            sanitized = f"doc_{sanitized}"
        return sanitized
    
    def create_collection(self, doc_id: str) -> chromadb.Collection:
        """Create or get a collection for a document."""
        safe_name = self._sanitize_collection_name(doc_id)
        return self.client.get_or_create_collection(name=safe_name)
    
    def delete_collection(self, doc_id: str) -> bool:
        """Delete a collection if it exists."""
        safe_name = self._sanitize_collection_name(doc_id)
        try:
            self.client.delete_collection(name=safe_name)
            logger.info(f"Deleted collection: {safe_name}")
            return True
        except Exception as e:
            logger.warning(f"Could not delete collection {safe_name}: {e}")
            return False
    
    def ingest_document(
        self, 
        doc_id: str, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Chunk, embed, and store a document.
        
        Args:
            doc_id: Unique identifier for the document
            text: Full text content to process
            metadata: Optional metadata to attach to each chunk
        
        Returns:
            Number of chunks created
        """
        logger.info(f"Ingesting document {doc_id} ({len(text)} chars)...")
        
        # 1. Split into chunks
        splitter = get_splitter()
        chunks = splitter.split_text(text)
        logger.info(f"Created {len(chunks)} chunks")
        
        if not chunks:
            logger.warning("No chunks created from text")
            return 0
        
        # 2. Generate embeddings
        embedder = get_embedder()
        logger.info("Generating embeddings...")
        embeddings = embedder.encode(chunks, show_progress_bar=False).tolist()
        
        # 3. Store in ChromaDB
        collection = self.create_collection(doc_id)
        
        # Clear existing data if re-ingesting
        try:
            existing = collection.count()
            if existing > 0:
                logger.info(f"Clearing {existing} existing chunks")
                collection.delete(where={"doc_id": doc_id})
        except:
            pass
        
        # Add chunks with metadata
        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        chunk_metadata = [
            {
                "chunk_index": i,
                "doc_id": doc_id,
                **(metadata or {})
            }
            for i in range(len(chunks))
        ]
        
        collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=chunk_metadata
        )
        
        logger.info(f"Successfully stored {len(chunks)} chunks in vector store")
        return len(chunks)
    
    def search(
        self, 
        doc_id: str, 
        query: str, 
        top_k: int = 5
    ) -> List[str]:
        """
        Semantic search for relevant chunks in a document.
        
        Args:
            doc_id: Document ID to search within
            query: User's question or search query
            top_k: Number of top results to return
        
        Returns:
            List of relevant text chunks, ordered by relevance
        """
        try:
            collection = self.client.get_collection(
                self._sanitize_collection_name(doc_id)
            )
        except Exception as e:
            logger.warning(f"Collection not found for {doc_id}: {e}")
            return []
        
        # Embed the query
        embedder = get_embedder()
        query_embedding = embedder.encode([query]).tolist()[0]
        
        # Search for similar chunks
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        if results and results["documents"]:
            chunks = results["documents"][0]
            logger.info(f"Found {len(chunks)} relevant chunks for query")
            return chunks
        
        return []
    
    def search_with_scores(
        self, 
        doc_id: str, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search with relevance scores included.
        
        Returns:
            List of dicts with 'text' and 'score' keys
        """
        try:
            collection = self.client.get_collection(
                self._sanitize_collection_name(doc_id)
            )
        except Exception as e:
            logger.warning(f"Collection not found for {doc_id}: {e}")
            return []
        
        embedder = get_embedder()
        query_embedding = embedder.encode([query]).tolist()[0]
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "distances"]
        )
        
        if results and results["documents"]:
            chunks = results["documents"][0]
            distances = results["distances"][0] if results.get("distances") else [0] * len(chunks)
            
            return [
                {
                    "text": chunk,
                    "score": 1 - dist  # Convert distance to similarity score
                }
                for chunk, dist in zip(chunks, distances)
            ]
        
        return []
    
    def get_collection_stats(self, doc_id: str) -> Dict[str, Any]:
        """Get statistics about a document's vector store."""
        try:
            collection = self.client.get_collection(
                self._sanitize_collection_name(doc_id)
            )
            return {
                "doc_id": doc_id,
                "chunk_count": collection.count(),
                "collection_name": self._sanitize_collection_name(doc_id)
            }
        except Exception as e:
            return {"doc_id": doc_id, "error": str(e)}
    
    def list_collections(self) -> List[str]:
        """List all document collections in the store."""
        collections = self.client.list_collections()
        return [c.name for c in collections]


# Singleton instance for use across the application
vector_store = VectorStoreService()

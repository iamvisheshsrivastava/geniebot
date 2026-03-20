"""
RAG (Retrieval Augmented Generation) system for GenieBot
Handles document loading, embedding, and retrieval
"""

import os
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
import faiss
from sentence_transformers import SentenceTransformer

from utils.logger import setup_logger
from utils.cache import EmbeddingCache

logger = setup_logger(__name__)


class RAGSystem:
    """Retrieval Augmented Generation system"""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 300,
        chunk_overlap: int = 50
    ):
        """
        Initialize RAG system
        
        Args:
            model_name: HuggingFace model name for embeddings
            chunk_size: Number of characters per chunk
            chunk_overlap: Character overlap between chunks
        """
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        logger.info(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        self.embedding_cache = EmbeddingCache()
        
        self.chunks: List[str] = []
        self.chunk_sources: List[str] = []
        self.embeddings: np.ndarray = np.array([])
        self.faiss_index = None
        
        logger.info("RAG system initialized")
    
    def load_documents(self, doc_dir: str) -> None:
        """
        Load documents from directory
        
        Args:
            doc_dir: Directory path containing .txt and .md files
        """
        logger.info(f"Loading documents from: {doc_dir}")
        
        doc_path = Path(doc_dir)
        if not doc_path.exists():
            logger.warning(f"Document directory not found: {doc_dir}")
            return
        
        documents = []
        for file_path in doc_path.glob("*"):
            if file_path.suffix in [".txt", ".md"]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        documents.append((file_path.name, content))
                        logger.debug(f"Loaded: {file_path.name}")
                except Exception as e:
                    logger.error(f"Error loading {file_path.name}: {e}")
        
        logger.info(f"Loaded {len(documents)} documents")
        
        # Split documents into chunks
        self._chunk_documents(documents)
    
    def _chunk_documents(self, documents: List[Tuple[str, str]]) -> None:
        """
        Split documents into overlapping chunks
        
        Args:
            documents: List of (filename, content) tuples
        """
        logger.info("Chunking documents...")
        
        self.chunks = []
        self.chunk_sources = []
        
        for filename, content in documents:
            # Split into chunks with overlap
            for i in range(0, len(content), self.chunk_size - self.chunk_overlap):
                chunk = content[i : i + self.chunk_size]
                if len(chunk.strip()) > 20:  # Skip very short chunks
                    self.chunks.append(chunk)
                    self.chunk_sources.append(filename)
        
        logger.info(f"Created {len(self.chunks)} chunks from documents")
        
        # Generate embeddings
        self._generate_embeddings()
    
    def _generate_embeddings(self) -> None:
        """Generate embeddings for all chunks and build FAISS index"""
        logger.info("Generating embeddings...")
        
        embeddings_list = []
        
        for i, chunk in enumerate(self.chunks):
            # Check cache first
            cached_embedding = self.embedding_cache.get(chunk)
            
            if cached_embedding is not None:
                embeddings_list.append(cached_embedding)
            else:
                # Generate embedding
                embedding = self.embedding_model.encode(chunk, convert_to_numpy=True)
                embeddings_list.append(embedding)
                self.embedding_cache.put(chunk, embedding)
            
            if (i + 1) % 10 == 0:
                logger.debug(f"Generated embeddings for {i + 1}/{len(self.chunks)} chunks")
        
        self.embeddings = np.array(embeddings_list).astype("float32")
        
        # Build FAISS index
        logger.info("Building FAISS index...")
        embedding_dim = self.embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(embedding_dim)
        self.faiss_index.add(self.embeddings)
        
        logger.info(f"FAISS index built with {self.faiss_index.ntotal} vectors")
        
        # Log cache stats
        cache_stats = self.embedding_cache.stats()
        logger.debug(f"Cache stats: {cache_stats}")
    
    def retrieve_chunks(self, query: str, top_k: int = 3) -> List[Tuple[str, str]]:
        """
        Retrieve top-k relevant chunks for a query
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
        
        Returns:
            List of (chunk_text, source_filename) tuples
        """
        if self.faiss_index is None or len(self.chunks) == 0:
            logger.warning("No documents loaded. Cannot retrieve chunks.")
            return []
        
        logger.debug(f"Retrieving chunks for query: {query[:50]}...")
        
        # Encode query
        query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)
        query_embedding = np.array([query_embedding]).astype("float32")
        
        # Search FAISS index
        distances, indices = self.faiss_index.search(query_embedding, min(top_k, len(self.chunks)))
        
        retrieved_chunks = []
        for idx in indices[0]:
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                source = self.chunk_sources[idx]
                retrieved_chunks.append((chunk, source))
        
        logger.debug(f"Retrieved {len(retrieved_chunks)} chunks")
        
        return retrieved_chunks
    
    def get_rag_context(self, query: str, top_k: int = 3) -> str:
        """
        Build context string from retrieved chunks for LLM
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
        
        Returns:
            Formatted context string with source attribution
        """
        chunks = self.retrieve_chunks(query, top_k)
        
        if not chunks:
            logger.warning("No relevant chunks found")
            return "No relevant documents found in the knowledge base."
        
        context = "Relevant context from documents:\n\n"
        
        for i, (chunk, source) in enumerate(chunks, 1):
            context += f"[Source {i}: {source}]\n"
            context += f"{chunk}\n\n"
        
        return context
    
    def get_source_chunks(self, query: str, top_k: int = 3) -> Dict[str, List[str]]:
        """
        Get source information for retrieved chunks
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
        
        Returns:
            Dictionary mapping source filenames to chunks
        """
        chunks = self.retrieve_chunks(query, top_k)
        sources = {}
        
        for chunk, source in chunks:
            if source not in sources:
                sources[source] = []
            sources[source].append(chunk[:100] + "...")
        
        return sources
    
    def has_documents(self) -> bool:
        """Check if documents are loaded"""
        return len(self.chunks) > 0
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        return {
            "total_chunks": len(self.chunks),
            "embedding_model": self.model_name,
            "chunk_size": self.chunk_size,
            "faiss_index_size": self.faiss_index.ntotal if self.faiss_index else 0,
            "cache_stats": self.embedding_cache.stats()
        }

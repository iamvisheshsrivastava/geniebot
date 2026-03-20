"""
QA interface combining RAG system with LLM
"""

from typing import Dict, List, Tuple
from .system import RAGSystem
from .llm import OllamaLLM
from utils.logger import setup_logger
from utils.cache import QueryCache

logger = setup_logger(__name__)


class RAGQA:
    """RAG-based Question Answering system"""
    
    def __init__(
        self,
        rag_system: RAGSystem,
        llm: OllamaLLM,
        use_cache: bool = True
    ):
        """
        Initialize RAG QA system
        
        Args:
            rag_system: RAG retrieval system
            llm: LLM for generation
            use_cache: Cache query responses
        """
        self.rag = rag_system
        self.llm = llm
        self.query_cache = QueryCache() if use_cache else None
        
        logger.info("RAG QA system initialized")
    
    def answer_question(
        self,
        question: str,
        use_cache: bool = True
    ) -> Dict[str, any]:
        """
        Answer a question using RAG
        
        Args:
            question: User question
            use_cache: Use cache if available
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        logger.info(f"Processing question: {question[:50]}...")
        
        # Check cache
        if use_cache and self.query_cache:
            cached_answer = self.query_cache.get(question)
            if cached_answer:
                logger.debug("Returning cached answer")
                return {
                    "answer": cached_answer,
                    "sources": [],
                    "cached": True
                }
        
        # Check if documents are loaded
        if not self.rag.has_documents():
            logger.warning("No documents loaded")
            return {
                "answer": "No documents loaded. Please add documents first.",
                "sources": [],
                "error": True
            }
        
        # Retrieve relevant chunks
        context = self.rag.get_rag_context(question, top_k=3)
        source_chunks = self.rag.get_source_chunks(question, top_k=3)
        
        # Build prompt for LLM
        system_prompt = (
            "You are a helpful AI assistant. "
            "Answer questions based on the provided context. "
            "Be concise and accurate. If you cannot find the answer in the context, say so."
        )
        
        prompt = f"""Based on the following context, answer the question concisely.

{context}

Question: {question}

Answer:"""
        
        # Generate answer using LLM
        answer = self.llm.generate(prompt, system_prompt=system_prompt)
        
        # Cache the result
        if use_cache and self.query_cache:
            self.query_cache.put(question, answer)
        
        logger.info("Question answered successfully")
        
        return {
            "answer": answer,
            "sources": source_chunks,
            "cached": False
        }
    
    def get_answer_with_sources(self, question: str) -> Tuple[str, Dict]:
        """
        Get answer with formatted source information
        
        Args:
            question: User question
        
        Returns:
            Tuple of (answer, sources_dict)
        """
        result = self.answer_question(question)
        return result["answer"], result.get("sources", {})
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        return {
            "rag_stats": self.rag.get_stats(),
            "llm_model": self.llm.model,
            "llm_available": self.llm.is_available(),
            "cache_size": self.query_cache.size() if self.query_cache else 0
        }

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
        
        # Build a strict prompt to avoid meta responses like
        # "based on the given context" in final user-facing output.
        system_prompt = (
            "You are GenieBot, a concise assistant for document-grounded answers. "
            "Use only the provided context. "
            "Return only the direct answer for the user. "
            "Do not mention prompts, context, documents, or your reasoning process. "
            "If the answer is not in the provided context, reply exactly: "
            "I could not find that in the loaded documents."
        )

        prompt = f"""Context:
{context}

Question: {question}

Instructions:
- Answer in 2 to 4 short sentences.
- Be specific and factual.
- Do not add preambles or explanations about how you answered.

Final Answer:"""
        
        # Generate answer using LLM
        answer = self.llm.generate(
            prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )

        # Clean up answer - remove any preamble if LLM included it
        if isinstance(answer, str):
            # Remove common preambles the LLM might add
            for preamble in ["**Answer:**", "Answer:", "Final Answer:", "Based on the context:"]:
                if answer.strip().lower().startswith(preamble.lower()):
                    answer = answer[len(preamble):].strip()
            # Take only first 1000 chars to prevent context bleeding
            answer = answer[:1000]

        # Do not cache or return failed model responses as normal answers.
        if isinstance(answer, str) and answer.strip().lower().startswith("error:"):
            logger.error(f"LLM generation failed for question '{question[:50]}...': {answer}")
            return {
                "answer": (
                    "I could not generate an answer right now because the local LLM is unavailable. "
                    "Please check Ollama/model status and try again."
                ),
                "sources": {},
                "cached": False,
                "error": True,
                "details": answer,
            }
        
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

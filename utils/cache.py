"""
Caching utility for GenieBot
Caches embeddings and query results to avoid recomputation
"""

import hashlib
import time
from typing import Optional, List, Dict, Any
import numpy as np
from .logger import setup_logger

logger = setup_logger(__name__)


class RateLimiter:
    """Simple per-user fixed-window rate limiter (in-memory, single process).

    GenieBot is a public bot with a shared OpenRouter key - without this,
    one user spamming /ask or image uploads can exhaust the free-tier quota
    for everyone. Not distributed-safe, but the bot only ever runs as one
    process on Render's free tier, so that's not a concern here.
    """

    def __init__(self, limit: int = 10, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        # user_id -> (window_expires_at, count_in_window)
        self._counters: Dict[int, tuple] = {}

    def allow(self, user_id: int) -> bool:
        """Return True if this request is allowed, False if the user is over their limit."""
        now = time.time()
        expires_at, count = self._counters.get(user_id, (now + self.window_seconds, 0))

        if expires_at < now:
            expires_at = now + self.window_seconds
            count = 0

        count += 1
        self._counters[user_id] = (expires_at, count)

        allowed = count <= self.limit
        if not allowed:
            logger.warning(f"Rate limit exceeded for user {user_id} ({count}/{self.limit} in window)")
        return allowed

    def seconds_until_reset(self, user_id: int) -> int:
        """Seconds remaining until this user's window resets."""
        expires_at, _ = self._counters.get(user_id, (0, 0))
        return max(0, int(expires_at - time.time()))


class EmbeddingCache:
    """Cache for text embeddings"""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize embedding cache
        
        Args:
            max_size: Maximum number of cached embeddings
        """
        self.max_size = max_size
        self.cache: Dict[str, np.ndarray] = {}
        self.access_count: Dict[str, int] = {}  # Track access frequency
    
    @staticmethod
    def _hash_text(text: str) -> str:
        """
        Hash text for cache key
        
        Args:
            text: Text to hash
        
        Returns:
            Hash string
        """
        return hashlib.md5(text.lower().encode()).hexdigest()
    
    def get(self, text: str) -> Optional[np.ndarray]:
        """
        Retrieve embedding from cache
        
        Args:
            text: Text to retrieve embedding for
        
        Returns:
            Embedding array or None if not cached
        """
        key = self._hash_text(text)
        
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            logger.debug(f"Cache hit for: {text[:50]}... (count: {self.access_count[key]})")
            return self.cache[key]
        
        return None
    
    def put(self, text: str, embedding: np.ndarray) -> None:
        """
        Store embedding in cache
        
        Args:
            text: Original text
            embedding: Embedding vector
        """
        if len(self.cache) >= self.max_size:
            # Remove least accessed item
            least_accessed = min(self.access_count, key=self.access_count.get)
            del self.cache[least_accessed]
            del self.access_count[least_accessed]
            logger.debug(f"Cache full. Removed least accessed item.")
        
        key = self._hash_text(text)
        self.cache[key] = embedding
        self.access_count[key] = 0
        logger.debug(f"Cached embedding for: {text[:50]}...")
    
    def clear(self) -> None:
        """Clear all cached embeddings"""
        self.cache.clear()
        self.access_count.clear()
        logger.info("Cache cleared")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_cached": len(self.cache),
            "max_size": self.max_size,
            "hit_rate_estimate": len([v for v in self.access_count.values() if v > 0]) / max(1, len(self.cache))
        }


class QueryCache:
    """Cache for query responses"""
    
    def __init__(self, max_size: int = 500):
        """
        Initialize query cache
        
        Args:
            max_size: Maximum number of cached queries
        """
        self.max_size = max_size
        self.cache: Dict[str, str] = {}
    
    @staticmethod
    def _hash_query(query: str) -> str:
        """
        Hash query for cache key
        
        Args:
            query: Query string
        
        Returns:
            Hash string
        """
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    def get(self, query: str) -> Optional[str]:
        """
        Retrieve cached response
        
        Args:
            query: Query string
        
        Returns:
            Cached response or None
        """
        key = self._hash_query(query)
        result = self.cache.get(key)
        
        if result:
            logger.debug(f"Query cache hit for: {query[:50]}...")
        
        return result
    
    def put(self, query: str, response: str) -> None:
        """
        Store response in cache
        
        Args:
            query: Query string
            response: Response text
        """
        if len(self.cache) >= self.max_size:
            # Remove first item (simple FIFO)
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        
        key = self._hash_query(query)
        self.cache[key] = response
        logger.debug(f"Cached response for: {query[:50]}...")
    
    def clear(self) -> None:
        """Clear all cached queries"""
        self.cache.clear()
        logger.info("Query cache cleared")
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)

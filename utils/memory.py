"""
User memory management for GenieBot
Maintains conversation history (last 3 interactions per user)
"""

from collections import OrderedDict
from typing import List, Dict
from datetime import datetime
from .logger import setup_logger

logger = setup_logger(__name__)


class UserMemory:
    """Manages user conversation history"""

    def __init__(self, max_history: int = 3, max_users: int = 5000):
        """
        Initialize user memory

        Args:
            max_history: Maximum number of interactions to store per user
            max_users: Maximum number of distinct users to keep history for.
                Least-recently-active user is evicted once this cap is hit,
                so the dict can't grow unbounded on a long-running process.
        """
        self.max_history = max_history
        self.max_users = max_users
        # user_id -> list of interactions. OrderedDict so we can evict the
        # least-recently-touched user in O(1) once we're at capacity.
        self.history: "OrderedDict[int, List[Dict]]" = OrderedDict()

    def add_interaction(
        self,
        user_id: int,
        query: str,
        response: str,
        interaction_type: str = "text"
    ) -> None:
        """
        Add an interaction to user history

        Args:
            user_id: Telegram user ID
            query: User's query/input
            response: Bot's response
            interaction_type: Type of interaction (text, image, etc.)
        """
        if user_id in self.history:
            self.history.move_to_end(user_id)
        else:
            self.history[user_id] = []
            if len(self.history) > self.max_users:
                evicted_id, _ = self.history.popitem(last=False)
                logger.debug(f"Evicted history for least-recently-active user {evicted_id}")

        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "type": interaction_type
        }

        self.history[user_id].append(interaction)

        # Keep only last max_history interactions
        if len(self.history[user_id]) > self.max_history:
            self.history[user_id].pop(0)

        logger.debug(f"Added interaction for user {user_id}")

    def get_history(self, user_id: int) -> List[Dict]:
        """
        Get full history for a user

        Args:
            user_id: Telegram user ID

        Returns:
            List of interactions
        """
        return self.history.get(user_id, [])

    def get_context(self, user_id: int) -> str:
        """
        Get formatted context for LLM from user history

        Args:
            user_id: Telegram user ID

        Returns:
            Formatted conversation context
        """
        history = self.get_history(user_id)
        if not history:
            return ""

        context = "Previous interactions:\n"
        for interaction in history:
            context += f"- Q: {interaction['query']}\n"
            context += f"  A: {interaction['response'][:100]}...\n"

        return context

    def clear_history(self, user_id: int) -> None:
        """
        Clear history for a user

        Args:
            user_id: Telegram user ID
        """
        if user_id in self.history:
            del self.history[user_id]
            logger.info(f"Cleared history for user {user_id}")

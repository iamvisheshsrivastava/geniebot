"""
Configuration module for GenieBot
Centralized settings management
"""

import os
from pathlib import Path
from typing import Optional

# Directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Environment variables
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma3:4b")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# RAG Configuration
RAG_CONFIG = {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "chunk_size": 300,
    "chunk_overlap": 50,
    "top_k_retrieval": 3,
}

# Vision Configuration
VISION_CONFIG = {
    "model_name": "Salesforce/blip-image-captioning-base",
    "num_tags": 3,
    "max_image_size": 512,
}

# Memory Configuration
MEMORY_CONFIG = {
    "max_history_per_user": 3,
    "max_total_users": 10000,
}

# Cache Configuration
CACHE_CONFIG = {
    "embedding_cache_size": 1000,
    "query_cache_size": 500,
    "enable_caching": True,
}

# LLM Configuration
LLM_CONFIG = {
    "timeout": 120,
    "temperature": 0.7,
    "max_tokens": None,
}

# Bot Configuration
BOT_CONFIG = {
    "max_message_length": 4000,  # Telegram limit
    "typing_timeout": 5,
    "error_retry_attempts": 3,
}

# Validation
def validate_config() -> bool:
    """
    Validate critical configuration
    
    Returns:
        True if valid, False otherwise
    """
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in environment")
        return False
    
    if not DATA_DIR.exists():
        print(f"WARNING: Data directory not found: {DATA_DIR}")
        DATA_DIR.mkdir(exist_ok=True)
    
    if not LOGS_DIR.exists():
        LOGS_DIR.mkdir(exist_ok=True)
    
    return True


def print_config():
    """Print current configuration"""
    print("\n" + "="*50)
    print("GenieBot Configuration")
    print("="*50)
    print(f"Base Directory: {BASE_DIR}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Logs Directory: {LOGS_DIR}")
    print(f"\nOllama:")
    print(f"  URL: {OLLAMA_BASE_URL}")
    print(f"  Model: {OLLAMA_MODEL}")
    print(f"\nRAG:")
    print(f"  Chunk Size: {RAG_CONFIG['chunk_size']}")
    print(f"  Top-K: {RAG_CONFIG['top_k_retrieval']}")
    print(f"\nCache:")
    print(f"  Enabled: {CACHE_CONFIG['enable_caching']}")
    print(f"  Embedding Cache Size: {CACHE_CONFIG['embedding_cache_size']}")
    print(f"  Query Cache Size: {CACHE_CONFIG['query_cache_size']}")
    print("="*50 + "\n")

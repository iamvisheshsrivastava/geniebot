"""
GenieBot - RAG & Vision AI Assistant for Telegram
Main application entry point
"""

import asyncio
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)

from rag import RAGSystem, OllamaLLM, RAGQA
from vision import ImageProcessor
from utils import UserMemory, setup_logger
from bot import (
    start,
    help_command,
    ask_command,
    image_command,
    handle_image,
    error_handler
)

# Setup logging
logger = setup_logger(__name__)

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
OLLAMA_MODEL_PRIORITY = os.getenv("OLLAMA_MODEL_PRIORITY", "")
OLLAMA_FALLBACK_MODELS = os.getenv("OLLAMA_FALLBACK_MODELS", "tinyllama")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DATA_DIR = Path("data")

# Validate configuration
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set in environment variables")
    raise ValueError("Please set TELEGRAM_BOT_TOKEN in .env file")

logger.info("="*50)


def _parse_model_list(raw_value: str) -> list[str]:
    """Parse comma-separated model names from env values."""
    return [m.strip() for m in raw_value.split(",") if m.strip()]


def _resolve_available_model(preferred: str, available: list[str]) -> Optional[str]:
    """Resolve preferred model to an installed Ollama tag if available."""
    preferred = (preferred or "").strip()
    if not preferred:
        return None

    preferred_lower = preferred.lower()
    for model in available:
        if model.lower() == preferred_lower:
            return model

    if ":" not in preferred:
        prefix = f"{preferred_lower}:"
        for model in available:
            if model.lower().startswith(prefix):
                return model

    return None
logger.info("GenieBot Starting")
logger.info("="*50)


def initialize_systems() -> dict:
    """
    Initialize all system components
    
    Returns:
        Dictionary with initialized systems
    """
    logger.info("Initializing systems...")
    
    # Initialize RAG System
    logger.info("Initializing RAG system...")
    rag_system = RAGSystem(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        chunk_size=300,
        chunk_overlap=50
    )
    
    # Load documents
    rag_system.load_documents(str(DATA_DIR))
    
    if not rag_system.has_documents():
        logger.warning("No documents loaded. RAG system will be limited.")
    else:
        logger.info(f"RAG system ready with {rag_system.get_stats()['total_chunks']} chunks")
    
    # Initialize LLM with priority and fallback model chain.
    logger.info(f"Initializing Ollama LLM (preferred: {OLLAMA_MODEL})...")
    llm = OllamaLLM(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        timeout=120
    )
    
    preferred_chain = [OLLAMA_MODEL] + _parse_model_list(OLLAMA_MODEL_PRIORITY)
    fallback_chain = _parse_model_list(OLLAMA_FALLBACK_MODELS)

    if not llm.is_available():
        logger.warning("Ollama not available. Make sure Ollama is running.")
        logger.info("Start Ollama with: ollama serve")
        logger.info("Pull model with: ollama pull llama2")
        llm.fallback_models = [m for m in fallback_chain if m and m != llm.model]
    else:
        models = llm.get_available_models()
        logger.info(f"Available Ollama models: {models}")

        selected_model = OLLAMA_MODEL
        for preferred in preferred_chain:
            resolved = _resolve_available_model(preferred, models)
            if resolved:
                selected_model = resolved
                break

        resolved_fallbacks = []
        for fallback in fallback_chain:
            resolved = _resolve_available_model(fallback, models)
            if resolved and resolved != selected_model and resolved not in resolved_fallbacks:
                resolved_fallbacks.append(resolved)

        llm.model = selected_model
        llm.fallback_models = resolved_fallbacks
        logger.info(f"Using Ollama model: {llm.model}")
        if llm.fallback_models:
            logger.info(f"Fallback models: {llm.fallback_models}")
        else:
            logger.info("Fallback models: none configured/available")
    
    # Initialize QA System
    logger.info("Initializing QA system...")
    qa_system = RAGQA(rag_system, llm, use_cache=True)
    
    # Initialize Vision System
    logger.info("Initializing vision system...")
    vision_processor = ImageProcessor(
        model_name="Salesforce/blip-image-captioning-base"
    )
    
    if not vision_processor.is_available():
        logger.warning("Vision model not available")
    else:
        logger.info("Vision system ready")
    
    # Initialize Memory
    user_memory = UserMemory(max_history=3)
    
    logger.info("All systems initialized successfully!")
    
    return {
        "rag_system": rag_system,
        "llm": llm,
        "qa_system": qa_system,
        "vision_processor": vision_processor,
        "user_memory": user_memory
    }


async def post_init(application: Application) -> None:
    """
    Post-initialization hook
    
    Args:
        application: Telegram application instance
    """
    await asyncio.sleep(0)
    logger.info("Bot is online and ready!")
    logger.info("Webhook/polling setup complete")


def main() -> None:
    """
    Main function - start the bot
    """
    logger.info("Creating Telegram application...")
    
    # Initialize systems
    systems = initialize_systems()
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Store systems in bot data
    application.bot_data.update(systems)
    
    # Add handlers
    logger.info("Registering command handlers...")
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(CommandHandler("image", image_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Post-initialization
    application.post_init = post_init
    
    logger.info("Handlers registered successfully")
    
    # Start bot
    logger.info("Starting bot polling...")
    logger.info("Press Ctrl+C to stop the bot")
    
    try:
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot encountered error: {e}")
        raise


if __name__ == "__main__":
    main()

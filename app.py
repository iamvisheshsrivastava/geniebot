"""
GenieBot - RAG & Vision AI Assistant for Telegram
Main application entry point
"""

import os
from pathlib import Path
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
    history_command,
    status_command,
    clear_cache_command,
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
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DATA_DIR = Path("data")

# Validate configuration
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set in environment variables")
    raise ValueError("Please set TELEGRAM_BOT_TOKEN in .env file")

logger.info("="*50)
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
    
    # Initialize LLM (Using Gemma 3.4b)
    logger.info(f"Initializing Ollama LLM (model: {OLLAMA_MODEL})...")
    logger.info(f"Using Ollama model: {OLLAMA_MODEL}")
    llm = OllamaLLM(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        timeout=120
    )
    
    if not llm.is_available():
        logger.warning("Ollama not available. Make sure Ollama is running.")
        logger.info("Start Ollama with: ollama serve")
        logger.info("Pull model with: ollama pull llama2")
    else:
        models = llm.get_available_models()
        logger.info(f"Available Ollama models: {models}")
    
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
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("clear_cache", clear_cache_command))
    
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

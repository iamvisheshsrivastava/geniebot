"""
Telegram bot handlers for GenieBot
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.logger import setup_logger

logger = setup_logger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Start command handler
    
    Args:
        update: Telegram update
        context: Handler context
    """
    user = update.effective_user
    logger.info(f"User {user.id} started bot")
    
    welcome_message = f"""
🤖 Welcome to **GenieBot**! 

I'm your AI-powered assistant with:
• 📚 RAG-based Question Answering from your documents
• 🖼️ Image Captioning & Tag Extraction
• 💾 Conversation Memory (last 3 interactions)
• ⚡ Fast and Cached Responses

*Choose what to do:*
/ask <query> - Ask any question about the documents
/image - Upload an image for analysis
/help - Show detailed help
/history - View your conversation history
/status - Check system status

Ready to help! What would you like to do?
"""
    
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Help command handler
    
    Args:
        update: Telegram update
        context: Handler context
    """
    logger.info(f"User {update.effective_user.id} requested help")
    
    help_text = """
📖 **GenieBot Help & Documentation**

**Available Commands:**

1️⃣ **/ask <question>**
   Ask any question about the documents
   Example: `/ask What is the return policy?`
   GenieBot will retrieve relevant context and provide an answer with sources

2️⃣ **/image**
   Upload an image for analysis
   GenieBot will generate a caption and extract relevant tags

3️⃣ **/history**
   View your last 3 interactions with the bot
   Helps maintain conversation context

4️⃣ **/status**
   Check system information:
   - Documents loaded
   - Models available
   - Cache statistics

5️⃣ **/clear_cache**
   Clear query cache to free memory

**Features:**

🎯 *RAG System*
   - Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
   - Vector DB: FAISS for fast retrieval
   - LLM: Ollama (llama2 or mistral)
   - Returns source chunks with answers

🖼️ *Vision System*
   - Model: Salesforce BLIP
   - Generates captions
   - Extracts tags

💾 *Memory Management*
   - Stores last 3 interactions per user
   - Uses for context in follow-up questions

⚡ *Caching*
   - Embeddings cached for efficiency
   - Query results cached
   - Speeds up repeated questions

**Tips:**
- Be specific in your questions for better results
- Upload clear, well-lit images
- Use /status to troubleshoot issues

Need more help? Check /start
"""
    
    await update.message.reply_text(help_text)


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Ask command handler - processes questions
    
    Args:
        update: Telegram update
        context: Handler context
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} used /ask command")
    
    # Get question from command arguments
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a question.\nUsage: /ask <your question>"
        )
        return
    
    question = " ".join(context.args)
    
    # Show loading message
    await update.message.reply_text("🔍 Searching and analyzing... This may take a moment.")
    
    try:
        # Get QA system from context
        qa_system = context.bot_data.get("qa_system")
        user_memory = context.bot_data.get("user_memory")
        
        if not qa_system:
            logger.error("QA system not available")
            await update.message.reply_text("❌ QA system not initialized")
            return
        
        # Get answer
        result = qa_system.answer_question(question)
        answer = result.get("answer", "No answer generated")
        sources = result.get("sources", {})
        
        # Store in user memory
        if user_memory:
            user_memory.add_interaction(user_id, question, answer, "text")
        
        # Format response
        response = f"🤖 **Answer:**\n{answer}"
        
        # Add sources if available
        if sources:
            response += "\n\n📚 **Sources:**\n"
            for source, chunks in sources.items():
                response += f"• {source}\n"
        
        # Split long responses to avoid Telegram limits.
        # If markdown parsing fails, fallback to plain text.
        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for part in parts:
                try:
                    await update.message.reply_text(part, parse_mode="Markdown")
                except Exception:
                    await update.message.reply_text(part)
        else:
            try:
                await update.message.reply_text(response, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(response)
        
        logger.info(f"Answer provided to user {user_id}")
    
    except Exception as e:
        logger.error(f"Error in ask command: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Image command handler - signals user to upload image
    
    Args:
        update: Telegram update
        context: Handler context
    """
    logger.info(f"User {update.effective_user.id} used /image command")
    
    await update.message.reply_text(
        "📸 Please upload an image for analysis.\n"
        "I will generate a caption and extract relevant tags.",
        parse_mode="Markdown"
    )


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle image uploads
    
    Args:
        update: Telegram update
        context: Handler context
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} uploaded an image")
    
    if not update.message.photo:
        return
    
    try:
        # Get image
        photo = update.message.photo[-1]
        photo_file = await photo.get_file()
        
        # Download image
        image_data = await photo_file.download_as_bytearray()
        
        # Show processing message
        processing_msg = await update.message.reply_text(
            "🔄 Processing image... Please wait."
        )
        
        # Get vision processor from context
        vision_processor = context.bot_data.get("vision_processor")
        user_memory = context.bot_data.get("user_memory")
        
        if not vision_processor:
            logger.error("Vision processor not available")
            await processing_msg.edit_text("❌ Vision processor not initialized")
            return
        
        # Process image
        result = vision_processor.process_image(bytes(image_data))
        
        if result.get("success"):
            caption = result.get("caption", "No caption generated")
            tags = result.get("tags", [])
            
            # Store in memory
            if user_memory:
                user_memory.add_interaction(user_id, "[Image Upload]", caption, "image")
            
            # Format response
            response = f"📸 **Caption:**\n{caption}\n\n"
            response += f"🏷️ **Tags:** {', '.join(tags)}"
            
            await processing_msg.edit_text(response, parse_mode="Markdown")
            logger.info(f"Image processed for user {user_id}")
        else:
            error = result.get("error", "Unknown error")
            await processing_msg.edit_text(f"❌ Error processing image: {error}")
            logger.error(f"Image processing error: {error}")
    
    except Exception as e:
        logger.error(f"Error handling image: {e}")
        await update.message.reply_text(f"❌ Error processing image: {str(e)}")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    History command - show user conversation history
    
    Args:
        update: Telegram update
        context: Handler context
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} requested history")
    
    user_memory = context.bot_data.get("user_memory")
    
    if not user_memory:
        await update.message.reply_text("❌ Memory system not available")
        return
    
    history = user_memory.get_history(user_id)
    
    if not history:
        await update.message.reply_text("📝 No conversation history yet.")
        return
    
    response = "📜 **Your Conversation History** (Last 3 interactions):\n\n"
    
    for i, interaction in enumerate(history, 1):
        timestamp = interaction.get("timestamp", "Unknown")
        query = interaction.get("query", "N/A")[:50]
        interaction_type = interaction.get("type", "text")
        
        response += f"{i}. [{interaction_type}] {query}...\n"
        response += f"   Time: {timestamp}\n\n"
    
    await update.message.reply_text(response, parse_mode="Markdown")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Status command - show system status
    
    Args:
        update: Telegram update
        context: Handler context
    """
    logger.info(f"User {update.effective_user.id} requested status")
    
    qa_system = context.bot_data.get("qa_system")
    vision_processor = context.bot_data.get("vision_processor")
    
    status = "📊 **System Status:**\n\n"
    
    if qa_system:
        system_info = qa_system.get_system_info()
        rag_stats = system_info.get("rag_stats", {})
        status += f"🧠 **RAG System:**\n"
        status += f"   Chunks: {rag_stats.get('total_chunks', 0)}\n"
        status += f"   LLM Model: {system_info.get('llm_model', 'N/A')}\n"
        status += f"   LLM Available: {'✅' if system_info.get('llm_available') else '❌'}\n"
        status += f"   Cache Size: {system_info.get('cache_size', 0)}\n\n"
    else:
        status += "🧠 **RAG System:** ❌ Not initialized\n\n"
    
    if vision_processor:
        status += f"👁️ **Vision System:** {'✅ Available' if vision_processor.is_available() else '❌ Not Available'}\n"
    else:
        status += "👁️ **Vision System:** ❌ Not initialized\n"
    
    await update.message.reply_text(status, parse_mode="Markdown")


async def clear_cache_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Clear cache command
    
    Args:
        update: Telegram update
        context: Handler context
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} cleared cache")
    
    qa_system = context.bot_data.get("qa_system")
    
    if qa_system:
        try:
            qa_system.query_cache.clear()
            await update.message.reply_text("✅ Cache cleared successfully!")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            await update.message.reply_text(f"❌ Error clearing cache: {str(e)}")
    else:
        await update.message.reply_text("❌ Cache system not available")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Error handler
    
    Args:
        update: Telegram update
        context: Handler context
    """
    logger.error(f"Update {update} caused error: {context.error}")

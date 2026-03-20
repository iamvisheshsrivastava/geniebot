"""Telegram command handlers for GenieBot."""

import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from utils.logger import setup_logger

logger = setup_logger(__name__)

MAX_TELEGRAM_MSG_LEN = 4000


async def _safe_reply_text(message, text: str, markdown: bool = True) -> None:
    """Reply with markdown first and fallback to plain text if parsing fails."""
    if markdown:
        try:
            await message.reply_text(text, parse_mode="Markdown")
            return
        except Exception:
            pass
    await message.reply_text(text)


async def _send_long_response(message, text: str, markdown: bool = True) -> None:
    """Split long responses to stay within Telegram limits."""
    if len(text) <= MAX_TELEGRAM_MSG_LEN:
        await _safe_reply_text(message, text, markdown=markdown)
        return

    for idx in range(0, len(text), MAX_TELEGRAM_MSG_LEN):
        chunk = text[idx : idx + MAX_TELEGRAM_MSG_LEN]
        await _safe_reply_text(message, chunk, markdown=markdown)


def _format_sources(sources: dict) -> str:
    """Format unique source file names for response display."""
    if not sources:
        return ""
    lines = ["", "📚 **Sources:**"]
    for source in sources.keys():
        lines.append(f"• {source}")
    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} started bot")

    text = (
        "🤖 Welcome to **GenieBot: RAG & Vision AI Assistant**\n\n"
        "Use these commands:\n"
        "• /ask <query> - Ask questions from local documents\n"
        "• /image - Upload an image for caption + tags\n"
        "• /help - Show usage instructions\n\n"
        "GenieBot keeps your last 3 interactions for better continuity."
    )
    await _safe_reply_text(update.message, text, markdown=True)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    logger.info(f"User {update.effective_user.id} requested help")

    help_text = (
        "📖 **How to use GenieBot**\n\n"
        "1. /ask <question>\n"
        "   Example: /ask What is the return policy?\n"
        "   GenieBot retrieves relevant document chunks and answers with sources.\n\n"
        "2. /image\n"
        "   Upload an image after this command.\n"
        "   GenieBot returns one caption and three tags.\n\n"
        "3. /start\n"
        "   Shows the quick command summary."
    )
    await _safe_reply_text(update.message, help_text, markdown=True)


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ask command using RAG QA."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} used /ask command")

    if not context.args:
        await _safe_reply_text(
            update.message,
            "❌ Please provide a question.\nUsage: /ask <your question>",
            markdown=False,
        )
        return

    question = " ".join(context.args)
    await _safe_reply_text(
        update.message,
        "🔍 Searching and analyzing... This may take a moment.",
        markdown=False,
    )

    qa_system = context.bot_data.get("qa_system")
    user_memory = context.bot_data.get("user_memory")
    if not qa_system:
        logger.error("QA system not available")
        await _safe_reply_text(update.message, "❌ QA system not initialized", markdown=False)
        return

    try:
        result = qa_system.answer_question(question)
        answer = result.get("answer", "No answer generated")
        sources = result.get("sources", {}) if not result.get("error") else {}

        if result.get("error"):
            logger.error(f"QA generation error for user {user_id}: {result.get('details', 'unknown')}")

        if user_memory:
            user_memory.add_interaction(user_id, question, answer, "text")

        response = f"🤖 **Answer:**\n{answer}{_format_sources(sources)}"
        await _send_long_response(update.message, response, markdown=True)
        logger.info(f"Answer provided to user {user_id}")
    except Exception as exc:
        logger.error(f"Error in ask command: {exc}")
        await _safe_reply_text(update.message, f"❌ Error: {exc}", markdown=False)


async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /image command."""
    logger.info(f"User {update.effective_user.id} used /image command")
    await _safe_reply_text(
        update.message,
        "📸 Please upload an image for analysis. I will return a caption and 3 tags.",
        markdown=False,
    )


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming photo messages for image captioning + tagging."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} uploaded an image")

    if not update.message.photo:
        return

    vision_processor = context.bot_data.get("vision_processor")
    user_memory = context.bot_data.get("user_memory")
    if not vision_processor:
        logger.error("Vision processor not available")
        await _safe_reply_text(update.message, "❌ Vision processor not initialized", markdown=False)
        return

    try:
        photo = update.message.photo[-1]
        photo_file = await photo.get_file()
        image_data = await photo_file.download_as_bytearray()

        processing_msg = await update.message.reply_text("🔄 Processing image... Please wait.")
        result = vision_processor.process_image(bytes(image_data))

        if not result.get("success"):
            error = result.get("error", "Unknown error")
            logger.error(f"Image processing error: {error}")
            await processing_msg.edit_text(f"❌ Error processing image: {error}")
            return

        caption = result.get("caption", "No caption generated")
        tags = result.get("tags", [])

        if user_memory:
            user_memory.add_interaction(user_id, "[Image Upload]", caption, "image")

        response = f"📸 **Caption:**\n{caption}\n\n🏷️ **Tags:** {', '.join(tags)}"
        try:
            await processing_msg.edit_text(response, parse_mode="Markdown")
        except Exception:
            await processing_msg.edit_text(response)

        logger.info(f"Image processed for user {user_id}")
    except Exception as exc:
        logger.error(f"Error handling image: {exc}")
        await _safe_reply_text(update.message, f"❌ Error processing image: {exc}", markdown=False)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global Telegram error handler."""
    await asyncio.sleep(0)
    logger.error(f"Update {update} caused error: {context.error}")

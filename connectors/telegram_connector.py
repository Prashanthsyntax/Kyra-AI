# connectors/telegram_connector.py
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def send_message(text: str):
    """Send a message to your Telegram chat."""
    async with Bot(token=TELEGRAM_BOT_TOKEN) as b:
        if len(text) <= 4096:
            await b.send_message(
                chat_id    = TELEGRAM_CHAT_ID,
                text       = text,
                parse_mode = "Markdown"
            )
        else:
            for i in range(0, len(text), 4096):
                await b.send_message(
                    chat_id    = TELEGRAM_CHAT_ID,
                    text       = text[i:i+4096],
                    parse_mode = "Markdown"
                )


def build_app(on_message_callback):
    """Build the Telegram polling app."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message and str(update.message.chat_id) == str(TELEGRAM_CHAT_ID):
            text    = update.message.text or ""
            user_id = str(update.message.from_user.id)   # ← real Telegram user ID
            print(f"[Kyra] Telegram message: {text}")
            await on_message_callback(text, user_id)      # ← pass user_id

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    return app
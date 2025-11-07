import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Бот успешно запущен через Render Webhook!")

def main():
    app = Application.builder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    webhook_url = f"{config.WEBHOOK_HOST}/{config.TRIBUTE_SECRET}"
    logger.info(f"Setting webhook to: {webhook_url}")

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", "10000")),
        url_path=config.TRIBUTE_SECRET,
        webhook_url=webhook_url,
    )

if __name__ == "__main__":
    main()

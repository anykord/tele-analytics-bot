import os
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import config


# -----------------------------
# ЛОГИРОВАНИЕ
# -----------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# -----------------------------
# ХЕНДЛЕРЫ
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Webhook бот запущен на Render!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Ты сказал: {text}")


# -----------------------------
# ОБРАБОТЧИК ДЛЯ ВХОДЯЩИХ ВЕБХУКОВ
# -----------------------------
async def handle_webhook(request):
    app: Application = request.app["bot_app"]
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(status=200)


async def on_startup(app):
    webhook_url = f"{config.WEBHOOK_HOST}/webhook"
    await app["bot_app"].bot.set_webhook(webhook_url)
    logger.info(f"✅ Webhook установлен: {webhook_url}")


async def on_shutdown(app):
    await app["bot_app"].shutdown()
    await app["bot_app"].stop()
    logger.info("🛑 Bot остановлен корректно.")


# -----------------------------
# ОСНОВНОЙ СЕРВЕР
# -----------------------------
async def main():
    # Создаем Telegram Application
    bot_app = Application.builder().token(config.BOT_TOKEN).build()

    # Добавляем хендлеры
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # aiohttp WebApp
    web_app = web.Application()
    web_app["bot_app"] = bot_app
    web_app.router.add_post("/webhook", handle_webhook)

    # хуки старта и остановки
    web_app.on_startup.append(on_startup)
    web_app.on_shutdown.append(on_shutdown)

    # запуск сервера
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logger.info(f"🚀 Webhook сервер запущен на порту {port}")

    # держим приложение живым
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.wait_until_closed()  # 🟡 УДАЛЕНО полностью
    # вместо этого просто ждем:
    await bot_app.running.wait()


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Бот остановлен вручную.")

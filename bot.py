import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import asyncio
import config
from telethon import TelegramClient
import openai

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация OpenAI
openai.api_key = config.OPENAI_API_KEY

# Инициализация Telethon клиента
if config.API_ID and config.API_HASH:
    telethon_client = TelegramClient("tele_analytics", config.API_ID, config.API_HASH)
else:
    telethon_client = None
    logger.warning("⚠️ Не задан API_ID или API_HASH — функции анализа Telegram будут отключены.")


# ---------- Команды ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие при /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name or 'друг'}! 👋\n"
        "Я бот для аналитики Telegram. Используй /help, чтобы узнать, что я умею."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Описание команд"""
    text = (
        "📊 *Доступные команды:*\n\n"
        "/analyze `<ссылка на канал>` — анализ Telegram-канала\n"
        "/plan — получить идеи контент-плана\n"
        "/filter — фильтрация постов по ключевым словам\n"
        "/help — справка\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def plan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация идей контента"""
    prompt = "Сгенерируй 5 идей для Telegram-контент-плана в нише маркетинга."
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты эксперт по контент-маркетингу."},
                {"role": "user", "content": prompt},
            ],
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Ошибка при генерации идей 😔")


async def analyze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Анализ Telegram-канала"""
    if not telethon_client:
        await update.message.reply_text("❌ Телеграм API не настроен, анализ недоступен.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Использование: /analyze <ссылка на канал>")
        return

    link = args[0]
    await update.message.reply_text(f"🔍 Анализирую {link}...")

    try:
        async with telethon_client:
            entity = await telethon_client.get_entity(link)
            title = getattr(entity, "title", "Неизвестно")
            participants = getattr(entity, "participants_count", "Неизвестно")

        text = f"📈 Канал: *{title}*\n👥 Подписчиков: {participants}"
        await update.message.reply_text(text, parse_mode="Markdown")

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Ошибка при анализе канала 😕")


async def filter_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фильтрация постов по ключевым словам"""
    keyboard = [
        [InlineKeyboardButton("Маркетинг", callback_data="filter_marketing")],
        [InlineKeyboardButton("Новости", callback_data="filter_news")],
        [InlineKeyboardButton("IT и технологии", callback_data="filter_it")],
    ]
    await update.message.reply_text(
        "Выберите категорию для фильтрации:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок"""
    query = update.callback_query
    await query.answer()
    choice = query.data
    await query.edit_message_text(f"Фильтр применён: {choice.replace('filter_', '').capitalize()}")


# ---------- Запуск ----------

def main():
    """Главная точка входа для Render"""
    app = Application.builder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("plan", plan_cmd))
    app.add_handler(CommandHandler("analyze", analyze_cmd))
    app.add_handler(CommandHandler("filter", filter_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Обработка сообщений с ссылками
    app.add_handler(MessageHandler(filters.Entity("url") | filters.Regex(r"t\.me/"), analyze_cmd))

    logger.info("✅ Бот запущен и готов к работе!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

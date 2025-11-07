import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)
from utils.parser import TeleParser
from utils.ai_analyzer import Analyzer
from utils.report import ReportGenerator
from db import DB
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = DB(config.DB_PATH)
parser = TeleParser(config.API_ID, config.API_HASH)
analyzer = Analyzer(config.OPENAI_API_KEY)
reporter = ReportGenerator()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.ensure_user(user.id)
    await update.message.reply_text(
        "Привет! Отправь ссылку на группу/канал для анализа (или /help). Тарифы: Фримиум / Базовый / Расширенный."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/analyze <link> — начать анализ\n"
        "/filter <keyword> — фильтр\n"
        "/plan — показать план\n"
        "/pay — оплатить подписку (через Tribute)"
    )


async def plan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    info = db.get_user(user.id)
    await update.message.reply_text(
        f"Ваш план: {info.get('plan')} | Лимит сообщений: {info.get('limit_value')} | Чатов: {info.get('chats')}"
    )


async def analyze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.ensure_user(user.id)

    # Получаем ссылку
    text = " ".join(context.args) if context.args else (
        update.message.reply_to_message.text if update.message.reply_to_message else ""
    )
    if not text:
        await update.message.reply_text("Укажите ссылку: /analyze https://t.me/yourgroup")
        return

    link = text.strip()
    info = db.get_user(user.id)
    await update.message.reply_text(f"Запущен парсинг {link}... (лимит {info.get('limit_value')} сообщений)")

    limit = info.get('limit_value')
    msgs = parser.parse_from_link(link, limit)
    await update.message.reply_text(f"Парсинг завершён: {len(msgs)} сообщений. Анализирую...")

    db.cache_messages(user.id, msgs)
    report = analyzer.analyze_messages(msgs, top_n=3)

    await update.message.reply_text(report.get('text', 'Анализ готов.'))

    plan = info.get('plan', 'freemium')

    if plan == "basic":
        pdf_path = reporter.to_pdf(f"Report {link}", report.get('text', ''), out_dir="reports")
        await update.message.reply_document(open(pdf_path, "rb"), caption="PDF-отчёт (Базовый план)")

    elif plan == "pro":
        csv_path = reporter.to_csv(msgs, out_dir="reports", title="analysis")
        json_path = reporter.to_json(msgs, out_dir="reports", title="analysis")
        await update.message.reply_document(open(csv_path, "rb"), caption="CSV (Расширенный)")
        await update.message.reply_document(open(json_path, "rb"), caption="JSON (Расширенный)")

    buttons = [
        [InlineKeyboardButton("Купить Базовый (PDF) — 1500₽/мес", callback_data="buy_basic")],
        [InlineKeyboardButton("Купить Расширенный (CSV/JSON) — 5000₽/мес", callback_data="buy_pro")],
    ]
    await update.message.reply_text("Опции:", reply_markup=InlineKeyboardMarkup(buttons))


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy_basic":
        await query.edit_message_text(
            "Для покупки перейдите в магазин @Tribute и оплатите план 'basic'. После оплаты бот активирует подписку."
        )
    elif query.data == "buy_pro":
        await query.edit_message_text(
            "Для покупки перейдите в магазин @Tribute и оплатите план 'pro'. После оплаты бот активирует подписку."
        )


async def filter_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("Использование: /filter <keyword> [since:YYYY-MM-DD] [from:@username]")
        return

    keyword = context.args[0]
    since, from_user = None, None

    for a in context.args[1:]:
        if a.startswith("since:"):
            since = a.split(":", 1)[1]
        elif a.startswith("from:"):
            from_user = a.split(":", 1)[1]

    results = db.search_messages(user.id, keyword, since, from_user)
    if not results:
        await update.message.reply_text("Ничего не найдено.")
        return

    text = "\n\n".join([f"{r['date']} {r['sender']}: {r['text'][:300]}" for r in results[:20]])
    await update.message.reply_text(text)


async def main():
    app = Application.builder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("plan", plan_cmd))
    app.add_handler(CommandHandler("analyze", analyze_cmd))
    app.add_handler(CommandHandler("filter", filter_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"t\.me/"), analyze_cmd))

    await app.initialize()
    await app.start()
    logger.info("Bot started successfully 🚀")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

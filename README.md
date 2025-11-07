# Tele Analytics Bot

Набросок SaaS Telegram-бота для анализа чатов.

## Быстрый старт (локально / VPS)
1. Клонировать проект.
2. Создать виртуальное окружение Python 3.11+:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Заполнить `config.py` или создать `.env` с ключами:
   - BOT_TOKEN
   - API_ID, API_HASH (Telethon)
   - OPENAI_API_KEY
   - GOOGLE_SERVICE_FILE (путь к google.json)
   - TRIBUTE_SECRET
   - WEBHOOK_HOST (адрес вашего сервера)
4. Запустить вебхук (Tribute):
   ```
   python webhook.py
   ```
5. Запустить бота:
   ```
   python bot.py
   ```

## Деплой на Render.com
- Создайте веб-сервис для webhook (порт 8000), командой `python webhook.py`.
- Создайте фоновый сервис (worker) для бота `python bot.py`.
- В ENV VARS в настройках Render добавьте ключи.

## @Tribute
- Настройте вебхук на `https://<your-app>/webhook/tribute` и добавьте заголовок `X-TRIBUTE-SECRET: <TRIBUTE_SECRET>`.

## Структура
- bot.py — основной бот (polling + callback)
- webhook.py — обработка платежей Tribute
- utils/parser.py — Telethon парсер
- utils/ai_analyzer.py — обёртка OpenAI
- utils/report.py — PDF/Sheets/CSV/JSON экспорт
- db.py — SQLite база

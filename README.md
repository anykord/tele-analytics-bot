# Tele Analytics Bot (CSV-based)

Updated version: Google Sheets removed. Reports exported as CSV/JSON/PDF files.

## Быстрый старт
1. Распакуйте проект.
2. Создайте виртуальное окружение Python 3.11+ и установите зависимости:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Заполните `.env` или `config.py`:
   - BOT_TOKEN
   - API_ID, API_HASH
   - OPENAI_API_KEY
   - TRIBUTE_SECRET
   - WEBHOOK_HOST
4. Запустите webhook:
   ```bash
   python webhook.py
   ```
5. Запустите бота:
   ```bash
   python bot.py
   ```

Файлы-отчёты сохраняются в папке `reports/` и отправляются пользователю в Telegram.


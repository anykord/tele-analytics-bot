import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "REPLACE_WITH_YOUR_BOT_TOKEN")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "REPLACE_API_HASH")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "REPLACE_OPENAI_KEY")
GOOGLE_SERVICE_FILE = os.getenv("GOOGLE_SERVICE_FILE", "google.json")
DB_PATH = os.getenv("DB_PATH", "tele_analytics.db")
TRIBUTE_SECRET = os.getenv("TRIBUTE_SECRET", "tribute_secret_example")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://your-render-app.onrender.com")

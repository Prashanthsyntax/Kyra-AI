import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY          = os.getenv("GROQ_API_KEY")
YOUR_PHONE_NUMBER     = os.getenv("YOUR_PHONE_NUMBER")
WHATSAPP_BOT_URL      = os.getenv("WHATSAPP_BOT_URL", "http://localhost:3000")

TWITTER_BEARER_TOKEN  = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_API_KEY       = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET    = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN  = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_TOKEN_FILE       = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
GOOGLE_CALENDAR_ID      = os.getenv("GOOGLE_CALENDAR_ID", "primary")

NEWS_API_KEY          = os.getenv("NEWS_API_KEY")
APP_PORT              = int(os.getenv("APP_PORT", 8000))
DIGEST_INTERVAL_HOURS = int(os.getenv("DIGEST_INTERVAL_HOURS", 2))

GROQ_MODEL = "llama-3.1-8b-instant"   # free, very fast on Groq

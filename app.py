import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
)
from bot import initialize_bot
from database import init_db
import os
from dotenv import load_dotenv
import requests

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))

# Initialize Flask app
app = Flask(__name__)

# Initialize bot application
application = Application.builder().token(BOT_TOKEN).build()
initialize_bot(application)

@app.route('/')
def index():
    return 'Bot is running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates"""
    if request.method == "POST":
        try:
            update = Update.de_json(request.get_json(), application.bot)
            application.process_update(update)
            return "ok"
        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)
            return str(e), 500
    return "ok"

if __name__ == "__main__":
    # Initialize database
    init_db()

    # Set the webhook URL
    webhook_url = f"{WEBHOOK_URL}/webhook"
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}")
    print(response.json())

    # Run Flask app
    app.run(host="0.0.0.0", port=PORT)

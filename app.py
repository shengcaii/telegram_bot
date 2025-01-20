#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from flask import Flask, request
import telegram
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from bot import initialize_bot
from database import init_db
import os
from dotenv import load_dotenv
import asyncio

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
application = None

def init_bot():
    """Initialize the bot application"""
    global application
    if not application:
        application = Application.builder().token(BOT_TOKEN).build()
        # Set up handlers
        initialize_bot(application)
    return application

@app.route('/')
def index():
    return 'Bot is running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates"""
    if request.method == "POST":
        try:
            # Get the update
            update = Update.de_json(request.get_json(), init_bot().bot)
            
            # Create an event loop for this request
            asyncio.set_event_loop(asyncio.new_event_loop())
            
            # Process update
            asyncio.get_event_loop().run_until_complete(
                application.process_update(update)
            )
            
            return "ok"
        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)
            return str(e), 500
    
    return "ok"

def setup_webhook():
    """Set up webhook using direct Telegram API"""
    try:
        bot = telegram.Bot(BOT_TOKEN)
        webhook_url = f"{WEBHOOK_URL}/webhook"
        
        # Create event loop for webhook setup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Set webhook
        loop.run_until_complete(bot.set_webhook(url=webhook_url))
        logger.info(f"Webhook set up successfully at {webhook_url}")
        
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Initialize bot and set up webhook
    init_bot()
    setup_webhook()
    
    # Run Flask app
    app.run(host="0.0.0.0", port=PORT)

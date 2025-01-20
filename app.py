#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

"""
Simple Bot to handle webhooks using Flask.
"""

import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from bot import (
    start, upload_start, search, my_resources, 
    delete_resource_command, upload_name, upload_category, 
    upload_location, upload_details, cancel
)
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

# States for conversation
NAME, CATEGORY, LOCATION, DETAILS = range(4)

# Initialize Flask app
app = Flask(__name__)

# Create global application instance
application = Application.builder().token(BOT_TOKEN).build()

def setup_handlers():
    """Set up all handlers for the application"""
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("myresources", my_resources))
    application.add_handler(CommandHandler("delete", delete_resource_command))

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("upload", upload_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, upload_name)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, upload_category)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, upload_location)],
            DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, upload_details)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(conv_handler)

@app.route("/")
def index():
    """Home route to check if the bot is running."""
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
async def webhook():
    """Handle incoming webhook updates."""
    try:
        # Parse the incoming update
        update = Update.de_json(request.get_json(force=True), application.bot)
        
        # Process the update asynchronously
        await application.process_update(update)
        
        return "ok"
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)
        return str(e), 500

async def initialize():
    """Initialize the bot application."""
    # Initialize database
    init_db()
    
    # Set up handlers
    setup_handlers()
    
    # Initialize the application
    await application.initialize()
    
    # Set webhook
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

def run():
    """Run the application."""
    # Create a new event loop and run the initialize function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(initialize())
    except Exception as e:
        logger.error(f"Error during initialization: {e}", exc_info=True)
    finally:
        loop.close()

if __name__ == "__main__":
    # Initialize the bot
    run()
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=PORT)
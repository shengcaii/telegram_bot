from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from bot import (
    start, upload_start, search, my_resources, 
    delete_resource_command, upload_name, upload_category, 
    upload_location, upload_details, cancel
)
from database import init_db
import os
from dotenv import load_dotenv
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Your Render URL

# States for conversation
NAME, CATEGORY, LOCATION, DETAILS = range(4)

app = Flask(__name__)

async def init_webhook():
    """Initialize bot and set webhook"""
    # Initialize bot application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("myresources", my_resources))
    application.add_handler(CommandHandler("delete", delete_resource_command))
    
    # Add conversation handler for upload
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

    # Set webhook
    webhook_url = f"{WEBHOOK_URL}/webhook"
    await application.bot.set_webhook(url=webhook_url)
    
    return application

# Initialize database
init_db()

# Create global application object
application = None

@app.route("/")
async def index():
    return "Bot is running!"

@app.route(f"/webhook", methods=["POST"])
async def webhook_handler():
    """Handle incoming webhook updates"""
    if request.method == "POST":
        await application.update_queue.put(
            Update.de_json(data=request.get_json(), bot=application.bot)
        )
        return "ok"
    
    return "Only POST requests are allowed"

# Initialize the bot and set webhook
@app.before_first_request
async def setup():
    global application
    application = await init_webhook()
    logger.info("Bot started and webhook set!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
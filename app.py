from flask import Flask, request, jsonify
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

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Your Render URL
PORT = int(os.getenv("PORT", 10000))

# States for conversation handler
NAME, CATEGORY, LOCATION, DETAILS = range(4)

app = Flask(__name__)

# Initialize bot application
application = Application.builder().token(BOT_TOKEN).build()

# Add handlers
def setup_handlers():
    """Set up all bot handlers"""
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

# Initialize handlers
setup_handlers()

# Initialize database
init_db()

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "alive",
        "message": "Telegram bot webhook is running!"
    })

@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
async def webhook():
    """Handle incoming webhook updates from Telegram"""
    if request.method == "POST":
        try:
            # Get the update data
            update_data = request.get_json()
            
            # Log incoming update
            logger.info(f"Received update: {update_data}")
            
            # Parse update from Telegram
            update = Update.de_json(update_data, application.bot)
            
            # Process update
            await application.process_update(update)
            
            return jsonify({"status": "success"})
            
        except Exception as e:
            logger.error(f"Error processing update: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    return jsonify({"status": "error", "message": "Method not allowed"}), 405

@app.route('/set_webhook', methods=['GET'])
async def set_webhook():
    """Endpoint to manually set up webhook"""
    try:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        await application.bot.set_webhook(url=webhook_url)
        
        webhook_info = await application.bot.get_webhook_info()
        logger.info(f"Webhook info: {webhook_info}")
        
        return jsonify({
            "status": "success",
            "message": "Webhook set up successfully",
            "webhook_url": webhook_url,
            "webhook_info": webhook_info.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error setting webhook: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
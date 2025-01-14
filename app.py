from flask import Flask, request, jsonify
from telegram import Bot, Update
import telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher
import os
from dotenv import load_dotenv
from database import init_db, add_member

# Load environment variables from .env file
load_dotenv()

# Replace with your bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# Initialize the database
init_db()

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    # Parse incoming update from Telegram
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return jsonify(success=True)

# Command handlers
def start(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Welcome to the connectorhook bot!")

def add_member_command(update, context):
    chat_id - update.message.chat_id
    try:
        name = context.args[0]
        role = context.args[1]
        add_member(name, role)
        context.bot.send_message(chat_id=chat_id, text=f"Member {name} with role {role} added successfully.")
    except IndexError:
        context.bot.send_message(chat_id=chat_id, text="Usage: /addmember <name> <role>")

# Set up the dispatcher
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("addmember", add_member_command))

# Start the Flask server
if __name__ == '__main__':
    # Set the webhook URL
    import requests
    WEBHOOK_URL = "https://telegram-bot-o9g1.onrender.com/webhook"

    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}")

    if response.status_code == 200:
        print("Webhook set successfully")
    else:
        print("Failed to set webhook")
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=5000)

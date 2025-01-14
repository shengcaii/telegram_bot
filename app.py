from flask import Flask, request, jsonify
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher, CallbackQueryHandler
import os
from dotenv import load_dotenv
from database import init_db, add_member, get_members

# Load environment variables from .env file
load_dotenv()

# Replace with your bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# Initialize the database
init_db()

# Initialize the dispatcher
dispatcher = Dispatcher(bot, None, workers=0)

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
    context.bot.send_message(chat_id=chat_id, text="Welcome to the team bot! Use /addmember <name> <role> to add a new member. Use /listmembers to list all members.")

def add_member_command(update, context):
    chat_id = update.message.chat_id
    keyboard = [
        [InlineKeyboardButton("Add Member", callback_data='add_member')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text="Press the button to add a new member.", reply_markup=reply_markup)

def button(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    if query.data == 'add_member':
        context.bot.send_message(chat_id=chat_id, text="Please enter the member's name and role in the format: /addmember <name> <role>")

def list_members_command(update, context):
    chat_id = update.message.chat_id
    members = get_members()
    if members:
        members_list = "\n".join([f"{name} - {role}" for name, role in members])
        context.bot.send_message(chat_id=chat_id, text=f"Team Members:\n{members_list}")
    else:
        context.bot.send_message(chat_id=chat_id, text="No members found.")

# Set up the dispatcher handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("addmember", add_member_command))
dispatcher.add_handler(CommandHandler("listmembers", list_members_command))
dispatcher.add_handler(CallbackQueryHandler(button))

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
    app.run(host='0.0.0.0', port=5000)
from telegram import Bot, Update
from telegram.ext import CommandHandler, Dispatcher, Updater
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch the bot token
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

# Initialize the bot
bot = Bot(token=TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Define command handlers
def start(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Welcome to the Resource Finder Bot! Use /help to see available commands.")

def help(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Available commands:\n/search <category> <location> - Search for resources\n/add <name> <category> <location> <contact> <details> - Add a new resource\n/update <id> <name> <category> <location> <contact> <details> - Update a resource\n/delete <id> - Delete a resource")

# Add command handlers to dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help))

# Start the bot
if __name__ == '__main__':
    print("Bot started!")
    updater.start_polling()
    updater.idle()

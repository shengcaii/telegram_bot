from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, ConversationHandler, ContextTypes
from database import dbupload, dbsearch
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Replace with your bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Define states for the conversation
NAME, CATEGORY, LOCATION, DETAILS = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.effective_user.first_name
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hey {first_name}! Welcome to the resource sharing bot.")

async def upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the name:")
    return NAME

async def upload_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the category:")
    return CATEGORY

async def upload_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['category'] = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the location:")
    return LOCATION

async def upload_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['location'] = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the details:")
    return DETAILS

async def upload_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['details'] = update.message.text
    name = context.user_data['name']
    category = context.user_data['category']
    location = context.user_data['location']
    contact = update.effective_user.id
    details = context.user_data['details']
    resource_id = dbupload(name, category, location, contact, details)
    if resource_id:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Uploaded successfully!")
    else:
       await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to upload. Please try again.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Cancelled.")

# search function
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        query = ' '.join(context.args)
        print(f"Searching for: {query}")
        results = dbsearch(query)
        if results:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Here are the results:")
            for result in results:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=result)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No results found.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a search query.")

def main():
    # Create the application
    application = (
        ApplicationBuilder()
        .token('7908797482:AAH5LvN9tNRf5dV8Bjt-iTLem1zUj34gUrA')
        .build()
    )

    # Add handlers to the application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("upload", upload_start)],
        states={
            NAME: [MessageHandler(filters.TEXT, upload_name)],
            CATEGORY: [MessageHandler(filters.TEXT, upload_category)],
            LOCATION: [MessageHandler(filters.TEXT, upload_location)],
            DETAILS: [MessageHandler(filters.TEXT, upload_details)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))
    application.add_handler(CommandHandler("search", search))

    # Run the application
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    application.idle()

if __name__ == '__main__':
    main()
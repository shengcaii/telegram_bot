from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from database import dbupload, dbsearch, dbdelete, db_get_data
import os
from dotenv import load_dotenv
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Replace with your bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = os.getenv("PORT")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


# Define states for the conversation
NAME, CATEGORY, LOCATION, DESCRIPTION = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.effective_user.first_name
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hey {first_name}! Welcome to the Ads Bot.\n\nUse /help to see the available commands.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response_text = f"You said: {update.message.text}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

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
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the description:")
    return DESCRIPTION

async def upload_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text
    name = context.user_data['name']
    category = context.user_data['category']
    location = context.user_data['location']
    contact = update.effective_user.id
    description = context.user_data['description']
    resource_id = dbupload(name, category, location, contact, description)
    
    if resource_id:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Uploaded successfully!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to upload. Please try again.")
    
    # Clear the user data
    context.user_data.clear()
    # End the conversation
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Cancelled.")

# search function
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        # Split the search terms and remove empty strings
        search_terms = [term.lower() for term in context.args if term.strip()]
        
        if not search_terms:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="⚠️ Please provide a valid search query."
            )
            return
        
        results = dbsearch(search_terms)
        
        if results:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=f"🔍 Found {len(results)} results for: {' '.join(search_terms)}"
            )
            
            for result in results:
                formatted_result = (
                    f"📍 *Name:* {result[0]}\n"
                    f"🏷️ *Category:* {result[1]}\n"
                    f"📌 *Location:* {result[2]}\n"
                    f"📝 *Details:* {result[3]}"
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=formatted_result,
                    parse_mode='Markdown'
                )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=f"❌ No results found for: {' '.join(search_terms)}"
            )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="⚠️ Please provide a search query. Example: /search sport yangon"
        )

async def my_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_ads = db_get_data(user_id)
    
    if not user_ads:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You don't have any ads yet."
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🗂 Here is your ads:"
    )
    
    for ads in user_ads:
        formatted_result = (
            f"🆔 *Ads ID:* {ads[0]}\n"
            f"📍 *Name:* {ads[1]}\n"
            f"🏷️ *Category:* {ads[2]}\n"
            f"📌 *Location:* {ads[3]}\n"
            f"📝 *Description:* {ads[4]}\n\n"
            f"_Use /delete {ads[0]} to remove this ads\n"
            f"_Use /update {ads[0]} to modify this ads"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=formatted_result,
            parse_mode='Markdown'
        )

async def delete_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Please provide ads ID. Example: /delete 123"
        )
        return
    
    try:
        ads_id = int(context.args[0])
        success, message = dbdelete(ads_id, update.effective_user.id)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{'✅' if success else '❌'} {message}"
        )
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Invalid ads ID. Please provide a valid one."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "🤖 *Available Commands:*\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/upload - Upload a new ads\n"
        "/search [category location] - Search for ads (e.g., /search sport yangon)\n"
        "/myads - View your own ads\n"
        "/delete [id] - Delete your ads by ID\n\n"
        "📝 *How to use:*\n"
        "1. Use /upload to add  new ads\n"
        "2. Use /search followed by keywords to find ads\n"
        "3. View your ads with /myads\n"
        "4. Delete your ads using /delete [ads_id]\n\n"
        "❓ Need more help? Contact [@admin](t.me/shengca1)"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def error_handler(update: Update, context):
    """Log errors and send a message to the user."""
    logger.error(f"Error occurred: {context.error}", exc_info=True)
    if update and update.message:
        await update.message.reply_text("An error occurred. Please try again later.")

def initialize_bot(application):
    """Initialize bot handlers"""
    print("Initializing bot...")
    # Add handlers to the provided application instance
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("upload", upload_start)],
        states={
            NAME: [MessageHandler(filters.TEXT, upload_name)],
            CATEGORY: [MessageHandler(filters.TEXT, upload_category)],
            LOCATION: [MessageHandler(filters.TEXT, upload_location)],
            DESCRIPTION: [MessageHandler(filters.TEXT, upload_description)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("myads", my_ads))
    application.add_handler(CommandHandler("delete", delete_ads))

    print("Bot initialized successfully!")
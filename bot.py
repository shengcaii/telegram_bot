from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from database import dbupload, dbsearch, dbdelete, db_get_data
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
PORT = os.getenv("PORT")

# Define states for the conversation
NAME, CATEGORY, LOCATION, DETAILS = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.effective_user.first_name
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hey {first_name}! Welcome to the advertisor bot.")

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
    return DETAILS

async def upload_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            
        print(f"Searching for terms: {search_terms}")
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

async def my_resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    resources = db_get_data(user_id)
    
    if not resources:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You haven't uploaded any resources yet."
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🗂 Your uploaded resources:"
    )
    
    for resource in resources:
        formatted_result = (
            f"🆔 *Resource ID:* {resource[0]}\n"
            f"📍 *Name:* {resource[1]}\n"
            f"🏷️ *Category:* {resource[2]}\n"
            f"📌 *Location:* {resource[3]}\n"
            f"📝 *Description:* {resource[4]}\n\n"
            f"_Use /delete {resource[0]} to remove this resource_\n"
            f"_Use /update {resource[0]} to modify this resource_"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=formatted_result,
            parse_mode='Markdown'
        )

async def delete_resource_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Please provide a resource ID. Example: /delete 123"
        )
        return
    
    try:
        resource_id = int(context.args[0])
        success, message = dbdelete(resource_id, update.effective_user.id)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{'✅' if success else '❌'} {message}"
        )
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Invalid resource ID. Please provide a valid number."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "🤖 *Available Commands:*\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/upload - Upload a new resource\n"
        "/search [terms] - Search for resources (e.g., /search sport yangon)\n"
        "/myresources - View your uploaded resources\n"
        "/delete [id] - Delete a resource by ID\n\n"
        "📝 *How to use:*\n"
        "1. Use /upload to add a new resource\n"
        "2. Use /search followed by keywords to find resources\n"
        "3. View your uploads with /myresources\n"
        "4. Delete your resources using /delete [resource_id]\n\n"
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
    # Add handlers to the provided application instance
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_error_handler(error_handler)
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
    application.add_handler(CommandHandler("myresources", my_resources))
    application.add_handler(CommandHandler("delete", delete_resource_command))

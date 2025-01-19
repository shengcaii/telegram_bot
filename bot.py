from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, ConversationHandler, ContextTypes
<<<<<<< HEAD
from database import dbupload, dbsearch
=======
from database import dbupload, dbsearch, get_user_resources, delete_resource
>>>>>>> c899748a2451722d99a1674cd36ae613e948908f
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
<<<<<<< HEAD
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hey {first_name}! Welcome to the resource sharing bot.")
=======
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hey {first_name}! Welcome to the advertisor bot.")
>>>>>>> c899748a2451722d99a1674cd36ae613e948908f

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
<<<<<<< HEAD
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the details:")
    return DETAILS

async def upload_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['details'] = update.message.text
=======
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the description:")
    return DETAILS

async def upload_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text
>>>>>>> c899748a2451722d99a1674cd36ae613e948908f
    name = context.user_data['name']
    category = context.user_data['category']
    location = context.user_data['location']
    contact = update.effective_user.id
<<<<<<< HEAD
    details = context.user_data['details']
    resource_id = dbupload(name, category, location, contact, details)
    if resource_id:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Uploaded successfully!")
    else:
       await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to upload. Please try again.")
=======
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
>>>>>>> c899748a2451722d99a1674cd36ae613e948908f

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Cancelled.")

# search function
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
<<<<<<< HEAD
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
=======
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
    resources = get_user_resources(user_id)
    
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
            f"📝 *Details:* {resource[4]}\n\n"
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
        success, message = delete_resource(resource_id, update.effective_user.id)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{'✅' if success else '❌'} {message}"
        )
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Invalid resource ID. Please provide a valid number."
        )
>>>>>>> c899748a2451722d99a1674cd36ae613e948908f

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
<<<<<<< HEAD
=======
    application.add_handler(CommandHandler("myresources", my_resources))
    application.add_handler(CommandHandler("delete", delete_resource_command))
>>>>>>> c899748a2451722d99a1674cd36ae613e948908f

    # Run the application
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    application.idle()

if __name__ == '__main__':
    main()
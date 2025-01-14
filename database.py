import sqlite3
from flask import Flask, request, jsonify
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher, CallbackQueryHandler
import os
from dotenv import load_dotenv

def init_db():
    try:
        conn = sqlite3.connect('team.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                document BLOB,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                video BLOB,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                image BLOB,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def add_member(name, role):
    try:
        conn = sqlite3.connect('team.db')
        c = conn.cursor()
        c.execute('INSERT INTO members (name, role) VALUES (?, ?)', (name, role))
        member_id = c.lastrowid
        conn.commit()
        return member_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def add_document(member_id, document):
    try:
        conn = sqlite3.connect('team.db')
        c = conn.cursor()
        c.execute('INSERT INTO documents (member_id, document) VALUES (?, ?)', (member_id, document))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def add_video(member_id, video):
    try:
        conn = sqlite3.connect('team.db')
        c = conn.cursor()
        c.execute('INSERT INTO videos (member_id, video) VALUES (?, ?)', (member_id, video))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def add_image(member_id, image):
    try:
        conn = sqlite3.connect('team.db')
        c = conn.cursor()
        c.execute('INSERT INTO images (member_id, image) VALUES (?, ?)', (member_id, image))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def get_members():
    try:
        conn = sqlite3.connect('team.db')
        c = conn.cursor()
        c.execute('SELECT id, name, role FROM members')
        members = c.fetchall()
        return members
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def get_documents(member_id):
    try:
        conn = sqlite3.connect('team.db')
        c = conn.cursor()
        c.execute('SELECT document FROM documents WHERE member_id = ?', (member_id,))
        documents = c.fetchall()
        return documents
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def get_videos(member_id):
    try:
        conn = sqlite3.connect('team.db')
        c = conn.cursor()
        c.execute('SELECT video FROM videos WHERE member_id = ?', (member_id,))
        videos = c.fetchall()
        return videos
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def get_images(member_id):
    try:
        conn = sqlite3.connect('team.db')
        c = conn.cursor()
        c.execute('SELECT image FROM images WHERE member_id = ?', (member_id,))
        images = c.fetchall()
        return images
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

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
        context.user_data['adding_member'] = True
        context.bot.send_message(chat_id=chat_id, text="Please enter the member's name and role in the format: <name> <role>")

def handle_message(update, context):
    chat_id = update.message.chat_id
    if context.user_data.get('adding_member'):
        try:
            name, role = update.message.text.split(' ', 1)
            member_id = add_member(name, role)
            context.user_data['member_id'] = member_id
            context.user_data['awaiting_document'] = True
            context.bot.send_message(chat_id=chat_id, text="Please send the document, image, or video.")
        except ValueError:
            context.bot.send_message(chat_id=chat_id, text="Invalid format. Please enter the member's name and role in the format: <name> <role>")
        context.user_data['adding_member'] = False
    elif context.user_data.get('awaiting_document'):
        document = update.message.document
        photo = update.message.photo[-1] if update.message.photo else None
        video = update.message.video
        member_id = context.user_data['member_id']
        if document:
            file_id = document.file_id
            file = context.bot.get_file(file_id)
            file_data = file.download_as_bytearray()
            add_document(member_id, file_data)
            context.bot.send_message(chat_id=chat_id, text=f"Document added successfully for member {member_id}.")
        elif photo:
            file_id = photo.file_id
            file = context.bot.get_file(file_id)
            file_data = file.download_as_bytearray()
            add_image(member_id, file_data)
            context.bot.send_message(chat_id=chat_id, text=f"Image added successfully for member {member_id}.")
        elif video:
            file_id = video.file_id
            file = context.bot.get_file(file_id)
            file_data = file.download_as_bytearray()
            add_video(member_id, file_data)
            context.bot.send_message(chat_id=chat_id, text=f"Video added successfully for member {member_id}.")
        else:
            context.bot.send_message(chat_id=chat_id, text="Please send a valid document, image, or video.")
        context.user_data['awaiting_document'] = False

def list_members_command(update, context):
    chat_id = update.message.chat_id
    members = get_members()
    if members:
        members_list = "\n".join([f"{name} - {role}" for _, name, role in members])
        context.bot.send_message(chat_id=chat_id, text=f"Team Members:\n{members_list}")
    else:
        context.bot.send_message(chat_id=chat_id, text="No members found.")

# Set up the dispatcher handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("addmember", add_member_command))
dispatcher.add_handler(CommandHandler("listmembers", list_members_command))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo | Filters.video, handle_message))
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
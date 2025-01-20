from bot import initialize_bot, BOT_TOKEN, PORT
from flask import Flask, request
from asgiref.wsgi import WsgiToAsgi
from telegram import Update
from telegram.ext import ApplicationBuilder
import requests
import os

bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
initialize_bot(bot_app)

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

@app.route('/')
def home():
    return {'status': 200, 'message': 'Bot is running'}

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Handle incoming webhook updates"""
    if request.method == "POST":
        try:
            data = request.get_json()
            print('Recieved update:', data)
            update = Update.de_json(data, bot_app.bot)
            await bot_app.process_update(update)
            return "ok"
        except Exception as e:
            return str(e), 500
    return "ok"

if __name__ == '__main__':
    # Set the webhook URL
    webhook_url = f"{WEBHOOK_URL}/webhook"
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}")
    print(response.json())

    # Run Flask app
    app.run(host="0.0.0.0", port=PORT)
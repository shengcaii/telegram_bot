from flask import Flask, request, jsonify
from telegram import Bot, Update
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace with your bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    # Parse incoming update from Telegram
    update = Update.de_json(request.get_json(force=True), bot)
    
    # Extract chat ID and message text
    chat_id = update.message.chat_id
    text = update.message.text

    # Respond to the user
    response_text = f"You said: {text}"
    bot.send_message(chat_id=chat_id, text=response_text)

    return jsonify(success=True)

# Start the Flask server
if __name__ == '__main__':
    # Set the webhook URL
    import requests
    WEBHOOK_URL = "https://your-deployed-app.com/webhook"
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}")
    print(response.json())
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=5000)

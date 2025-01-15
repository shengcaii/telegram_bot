from flask import Flask, request, jsonify
from database import init_db
import bot  # Import the bot module to ensure it runs

app = Flask(__name__)

# Initialize the database
init_db()

@app.route('/')
def home():
    return "Hello from telegram bot!"

if __name__ == "__main__":
    # Start the bot
    bot.updater.start_polling()
    print("Bot started!")
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000)
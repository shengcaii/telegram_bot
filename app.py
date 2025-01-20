from bot import initialize_bot, BOT_TOKEN
from flask import Flask
from telegram.ext import ApplicationBuilder

app = Flask(__name__)
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
initialize_bot(bot_app)

@app.get('/')
def home():
    return {'status':200, 'message': 'Bot is running'}



if __name__ == '__main__':
    app.run()
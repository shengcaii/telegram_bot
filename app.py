from bot import initialize_bot, BOT_TOKEN, PORT, WEBHOOK_URL
from flask import Flask, request, Response
from asgiref.wsgi import WsgiToAsgi
from telegram import Update
from telegram.ext import ApplicationBuilder
import asyncio
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask and PTB Application
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()
initialize_bot(application)


# Convert flask appp to asgi
asgi_app = WsgiToAsgi(app)
async def setup_webhook():
    await application.initialize()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    await application.start()

@app.route('/')
def home():
    return {'status': 200, 'message': 'Bot is running'}

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Handle incoming webhook updates"""
    if request.method == "POST":
        try:
            json_data =  request.get_json()
            print('Recieved update:', json_data)
            update = Update.de_json(json_data, application.bot)
            await application.update_queue.put(update)
            return Response(status=200)
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return Response(status=500)
    return "ok"

async def main():
    # Run application
    async with application:
        await application.start()
        await setup_webhook()
        await application.stop()

# Ensure the event loop is properly managed
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(main())
    else:
        asyncio.run(main())
except RuntimeError as e:
    if "There is no current event loop in thread" in str(e):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    else:
        raise
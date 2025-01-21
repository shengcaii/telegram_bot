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

async def main():
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
            json_data = await request.get_json()
            print('Recieved update:', json_data)
            update = Update.de_json(json_data, application.bot)
            await application.update_queue.put(update)
            return Response(status=200)
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return Response(status=500)
    return "ok"

if __name__ == '__main__':
    # Convert flask appp to asgi
    asgi_app = WsgiToAsgi(app)

    # Start everything
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

    # Run with Uvicorn
    uvicorn.run(
        app=asgi_app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
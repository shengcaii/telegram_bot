from bot import initialize_bot, BOT_TOKEN
from telegram.ext import ApplicationBuilder

# Initialize the bot application
application = ApplicationBuilder().token(str(BOT_TOKEN)).build()
initialize_bot(application)

def main():
    application.run_polling()

if __name__ == "__main__":
    main()
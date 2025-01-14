# Description: Check the webhook info of the bot

import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace with your bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Get webhook info
response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
print(response.json())

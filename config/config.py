import os
from dotenv import load_dotenv

load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
REGION = "europe"
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

import os
from dotenv import load_dotenv

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
REGION = "europe"
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
FILE_XLS = "data/player_stats.xlsx"
DEFAULT_NUMBER_OF_GAMES = 20
USERS_FILE = "data/users.json"

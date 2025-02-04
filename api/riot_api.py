import requests
from config.config import RIOT_API_KEY, REGION

BASE_URL = f"https://{REGION}.api.riotgames.com"

def get_puuid(game_name, tag):
    url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag}"
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    return response.json().get("puuid") if response.status_code == 200 else None

def get_match_history(puuid, count=5):
    url = f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    return response.json() if response.status_code == 200 else []

def get_match_details(match_id):
    url = f"{BASE_URL}/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    return response.json() if response.status_code == 200 else None

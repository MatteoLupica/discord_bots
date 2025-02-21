import requests
from config.config import RIOT_API_KEY, REGION, DEFAULT_NUMBER_OF_GAMES

BASE_URL = f"https://{REGION}.api.riotgames.com"

QUEUE_MAPPING = {
    420: "Solo/Q",  # Ranked Solo/Duo
    440: "Flex",    # Ranked Flex
    0: "Scrim",     # Custom Matches
}

def get_puuid(game_name, tag):
    url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag}"
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    if response.status_code == 200:
        return response.json().get("puuid")
    return None

def get_match_history(puuid, count=DEFAULT_NUMBER_OF_GAMES, start=0):
    queue_params = "&queue=420&queue=440&queue=0"
    url = f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}{queue_params}"
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    if response.status_code == 200:
        return response.json()
    return []

def get_match_details(match_id, api_key=None, region=None):
    if api_key is None:
        from config.config import RIOT_API_KEY
        api_key = RIOT_API_KEY
    if region is None:
        from config.config import REGION
        region = REGION
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers={"X-Riot-Token": api_key})
    if response.status_code != 200:
        return None
    response_data = response.json()
    queue_id = response_data["info"].get("queueId", -1)
    queue_type = QUEUE_MAPPING.get(queue_id, "Other")
    response_data["info"]["queueType"] = queue_type
    return response_data

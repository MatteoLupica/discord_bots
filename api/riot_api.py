import requests
from config.config import RIOT_API_KEY, REGION, DEFAULT_NUMBER_OF_GAMES

BASE_URL = f"https://{REGION}.api.riotgames.com"

# Queue IDs for classification
QUEUE_MAPPING = {
    420: "Solo/Q",  # Ranked Solo/Duo
    440: "Flex",    # Ranked Flex
    0: "Scrim",     # Custom Matches
}

def get_puuid(game_name, tag):
    """Get the PUUID of a player given their Riot ID."""
    url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag}"
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    return response.json().get("puuid") if response.status_code == 200 else None

def get_match_history(puuid, count=DEFAULT_NUMBER_OF_GAMES, start=0):
    """
    Get match IDs for a player's recent matches.
    Fetches Solo/Q, Flex, and Scrim (Custom) matches only.
    Supports pagination with 'start'.
    """
    queue_params = "&queue=420&queue=440&queue=0"  
    url = f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}{queue_params}"
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    
    return response.json() if response.status_code == 200 else []


def get_match_details(match_id):
    """Get full match details by match ID, including queue type classification."""
    url = f"{BASE_URL}/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    response_data = response.json()

    if response.status_code != 200:
        return None

    # Extract queue type
    queue_id = response_data["info"].get("queueId", -1)
    queue_type = QUEUE_MAPPING.get(queue_id, "Other")  # Default to "Other" if not in mapping

    # Add queueType to match details
    response_data["info"]["queueType"] = queue_type
    return response_data

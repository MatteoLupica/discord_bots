import json
import os

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"players": {}, "matches": {}}
    
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def register_player(discord_id, game_name, tag, role):
    data = load_data()
    data["players"][discord_id] = {"game_name": game_name, "tag": tag, "role": role}
    save_data(data)

def get_registered_players():
    return load_data()["players"]

def save_match(discord_id, match_id, game_mode, champion, role, kills, deaths, assists, win):
    data = load_data()
    if discord_id not in data["matches"]:
        data["matches"][discord_id] = []
    
    data["matches"][discord_id].append({
        "match_id": match_id,
        "game_mode": game_mode,
        "champion": champion,
        "role": role,
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "win": win
    })
    save_data(data)

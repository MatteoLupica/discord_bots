from api.riot_api import get_puuid, get_match_history, get_match_details
from role_stats import get_role_class

def get_last_n_match_ids(game_name, tag, num_matches):
    puuid = get_puuid(game_name, tag)
    if not puuid:
        return None, "Summoner not found"
    match_ids = get_match_history(puuid, count=num_matches)
    if not match_ids or len(match_ids) < num_matches:
        return None, "Not enough matches found"
    return match_ids, None

def get_match_stats(game_name, tag, match_id):
    puuid = get_puuid(game_name, tag)
    match_data = get_match_details(match_id)
    if not match_data or "info" not in match_data or "participants" not in match_data["info"]:
        return None, "Error fetching match data"
    participant = next((p for p in match_data["info"]["participants"] if p["puuid"] == puuid), None)
    if not participant:
        return None, "Summoner not found in match"
    team = [p for p in match_data["info"]["participants"] if p["teamId"] == participant["teamId"]]
    game_duration = match_data["info"]["gameDuration"]
    player_stats = get_role_class(participant, team, game_duration)
    return player_stats, None

from api.riot_api import get_puuid, get_match_history, get_match_details
from role_stats import TopStats, JungleStats, MidStats, ADCStats, SupportStats, PlayerStats, get_role_class
from bot import bot
from config.config import DISCORD_TOKEN

def test():
    print("🔍 Test API Riot Games")
    game_name = "name"
    tag = "tag"

    print(f"🔎 Cercando PUUID per {game_name}#{tag}...")

    puuid = get_puuid(game_name, tag)
    if not puuid:
        print("❌ Giocatore non trovato!")
        return

    print(f"✅ PUUID trovato: {puuid}\n")

    match_ids = get_match_history(puuid, count=3)
    if not match_ids:
        print("❌ Nessuna partita trovata!")
        return
    
    for match_id in match_ids:
        print(f"🆔 Match ID: {match_id}")

        # Ottenere i dettagli della partita
        match_data = get_match_details(match_id)
        
        if not match_data or "info" not in match_data or "participants" not in match_data["info"]:
            print(f"⚠️ Impossibile recuperare i dettagli della partita {match_id}!")
            continue

        # Trova il giocatore nei dettagli della partita
        participant = next((p for p in match_data["info"]["participants"] if p["puuid"] == puuid), None)

        if not participant:
            print(f"⚠️ Giocatore non trovato nella partita {match_id}.")
            continue

        team = [p for p in match_data["info"]["participants"] if p["teamId"] == participant["teamId"]]
        game_duration = match_data["info"]["gameDuration"]

        # Creare la classe in base al ruolo e stampare le statistiche
        player_stats = get_role_class(participant, team, game_duration)
        player_stats.print_stats()

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
    #test()

from api.riot_api import get_puuid, get_match_history, get_match_details
from bot import bot 

def test():
    print("🔍 Test API Riot Games")

    # Chiedi all'utente di inserire il nome e il tag del giocatore
    game_name = input("Inserisci il nome del giocatore: ")
    tag = input("Inserisci il tag (es. EUW): ")

    print(f"🔎 Cercando PUUID per {game_name}#{tag}...")

    # Ottenere il PUUID del giocatore
    puuid = get_puuid(game_name, tag)
    if not puuid:
        print("❌ Giocatore non trovato!")
        return

    print(f"✅ PUUID trovato: {puuid}\n")

    # Ottenere la cronologia delle partite
    match_ids = get_match_history(puuid, count=3)  # Ultime 3 partite
    if not match_ids:
        print("❌ Nessuna partita trovata!")
        return

    print(f"📜 Ultime {len(match_ids)} partite trovate:")
    
    for match_id in match_ids:
        print(f"🆔 Match ID: {match_id}")

        # Ottenere i dettagli della partita
        match_data = get_match_details(match_id)
        if not match_data:
            print("⚠️ Impossibile recuperare i dettagli della partita!")
            continue

        # Trova il giocatore nei dettagli della partita
        participant = next(p for p in match_data["info"]["participants"] if p["puuid"] == puuid)

        # Estrai statistiche della partita
        game_mode = match_data["info"]["gameMode"]
        champion = participant["championName"]
        kills = participant["kills"]
        deaths = participant["deaths"]
        assists = participant["assists"]
        win = "✅ Vittoria" if participant["win"] else "❌ Sconfitta"

        # Stampa i risultati
        print(f"🎮 Modalità: {game_mode}")
        print(f"🏆 Campione: {champion}")
        print(f"⚔️ KDA: {kills}/{deaths}/{assists}")
        print(f"🏅 Esito: {win}\n")

if __name__ == "__main__":
    bot.run()

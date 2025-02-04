import discord
from discord.ext import commands, tasks
from api.riot_api import get_puuid, get_match_history, get_match_details
from data.data_manager import register_player, get_registered_players, save_match, load_data
from config import DISCORD_BOT_TOKEN, CHANNEL_ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} è online!")
    daily_update.start()

@bot.command()
async def register(ctx, game_name, tag, role):
    """Registra un giocatore con il suo ruolo e nome in game."""
    register_player(str(ctx.author.id), game_name, tag, role)
    await ctx.send(f"✅ {ctx.author.mention}, registrato come {game_name}#{tag} con ruolo {role}!")

@tasks.loop(hours=24)
async def daily_update():
    """Aggiorna le partite ogni giorno."""
    players = get_registered_players()
    for discord_id, player in players.items():
        puuid = get_puuid(player["game_name"], player["tag"])
        if not puuid:
            continue

        matches = get_match_history(puuid, 5)
        for match_id in matches:
            match_data = get_match_details(match_id)
            if not match_data:
                continue

            participant = next(p for p in match_data["info"]["participants"] if p["puuid"] == puuid)
            save_match(discord_id, match_id, match_data["info"]["gameMode"], participant["championName"], 
                       player["role"], participant["kills"], participant["deaths"], participant["assists"], participant["win"])
    
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("📢 Aggiornamento giornaliero completato!")

@bot.command()
async def stats(ctx):
    """Mostra le statistiche delle partite recenti."""
    data = load_data()
    discord_id = str(ctx.author.id)

    if discord_id not in data["matches"]:
        await ctx.send("❌ Nessuna partita trovata!")
        return
    
    matches = data["matches"][discord_id]
    response = "📊 **Statistiche Recenti**:\n"
    for match in matches[-5:]:
        response += f"🛡️ **{match['champion']} ({match['role']})**\n"
        response += f"🎮 Modalità: {match['game_mode']}\n"
        response += f"🔪 KDA: {match['kills']}/{match['deaths']}/{match['assists']} - {'✅ Vittoria' if match['win'] else '❌ Sconfitta'}\n\n"
    
    await ctx.send(response)

@bot.command()
async def compare(ctx):
    """Confronta le statistiche delle ultime partite."""
    data = load_data()
    discord_id = str(ctx.author.id)

    if discord_id not in data["matches"]:
        await ctx.send("❌ Nessuna partita trovata!")
        return

    matches = data["matches"][discord_id][-5:]
    avg_kills = sum(m["kills"] for m in matches) / len(matches)
    avg_deaths = sum(m["deaths"] for m in matches) / len(matches)
    avg_assists = sum(m["assists"] for m in matches) / len(matches)
    win_rate = sum(1 for m in matches if m["win"]) / len(matches) * 100

    response = f"📊 **Confronto delle ultime {len(matches)} partite**:\n"
    response += f"🔪 KDA medio: {avg_kills:.1f}/{avg_deaths:.1f}/{avg_assists:.1f}\n"
    response += f"🏆 Win Rate: {win_rate:.1f}%\n"

    await ctx.send(response)

bot.run(DISCORD_BOT_TOKEN)

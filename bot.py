import discord
from discord.ext import commands, tasks
from api.riot_api import get_puuid, get_match_history, get_match_details
from role_stats import TopStats, JungleStats, MidStats, ADCStats, SupportStats, PlayerStats, get_role_class
from data.data_manager import register_player, get_registered_players, save_match, load_data
from config.config import CHANNEL_ID

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} è online!")

@bot.command()
async def register(ctx, game_name: str, tag: str, role: str):
    """Permette agli utenti di registrarsi con il proprio nome di gioco, tag e ruolo."""
    discord_id = str(ctx.author.id)  # ID univoco dell'utente su Discord

    register_player(discord_id, game_name, tag, role)

    await ctx.send(f"✅ **{ctx.author.name}** registrato con successo come **{game_name}#{tag}** con ruolo **{role}**!")


@bot.command()
async def stats(ctx, *args):
    """Mostra le statistiche dell'ultimo game di un giocatore. Se non viene fornito alcun parametro, mostra il proprio ultimo game."""
    
    # Caricare i giocatori registrati
    registered_players = get_registered_players()

    if not args:  # Se l'utente non ha fornito argomenti, usiamo il suo profilo registrato
        discord_id = str(ctx.author.id)  # Ottenere l'ID Discord dell'utente
        if discord_id in registered_players:
            game_name = registered_players[discord_id]["game_name"]
            tag = registered_players[discord_id]["tag"]
            await ctx.send(f"📌 Recuperando l'ultimo game per **{game_name}#{tag}**...")
        else:
            await ctx.send("❌ Non sei registrato! Usa `!register NomeGiocatore#Tag Ruolo` per registrarti.")
            return
    else:  
        # Se l'utente ha fornito un nome, usiamo quello
        full_input = " ".join(args)
        if "#" not in full_input:
            await ctx.send("❌ Formato errato! Usa `Nome Giocatore#Tag`.")
            return
        game_name, tag = full_input.rsplit("#", 1)
        game_name, tag = game_name.strip(), tag.strip()

    await ctx.send(f"🔍 Cercando statistiche per **{game_name}#{tag}**...")
    # Recupero il PUUID
    puuid = get_puuid(game_name, tag)
    if not puuid:
        await ctx.send("❌ Giocatore non trovato!")
        return

    # Otteniamo l'ultimo match
    match_ids = get_match_history(puuid, count=1)  # Ottiene solo l'ultimo match
    if not match_ids:
        await ctx.send(f"❌ Nessuna partita trovata per **{game_name}#{tag}**!")
        return

    match_id = match_ids[0]
    match_data = get_match_details(match_id)

    if not match_data or "info" not in match_data or "participants" not in match_data["info"]:
        await ctx.send(f"⚠️ Errore nel recupero dettagli della partita `{match_id}`.")
        return

    participant = next((p for p in match_data["info"]["participants"] if p["puuid"] == puuid), None)
    if not participant:
        await ctx.send(f"⚠️ `{game_name}` non trovato nella partita `{match_id}`.")
        return

    team = [p for p in match_data["info"]["participants"] if p["teamId"] == participant["teamId"]]
    game_duration = match_data["info"]["gameDuration"]

    # Creare la classe in base al ruolo
    player_stats = get_role_class(participant, team, game_duration)

    # Creazione dell'embed Discord
    embed = discord.Embed(title=f"📊 Statistiche per {game_name} ({tag}) - {player_stats.champion}", color=0x00ff00)
    embed.add_field(name="🏅 Esito", value="✅ Vittoria" if player_stats.win else "❌ Sconfitta", inline=True)
    embed.add_field(name="⚔️ KDA", value=f"{player_stats.kills}/{player_stats.deaths}/{player_stats.assists}", inline=True)
    embed.add_field(name="🎮 Ruolo", value=player_stats.role, inline=True)

    # Aggiungere statistiche in base al ruolo
    if isinstance(player_stats, TopStats):
        embed.add_field(name="📈 CSPM", value=f"{player_stats.cspm:.2f}", inline=True)
        embed.add_field(name="🔥 DPM", value=f"{player_stats.dpm:.2f}", inline=True)
        embed.add_field(name="🛡️ Solo Kills", value=player_stats.solo_kills, inline=True)
        embed.add_field(name="💰 Gold Diff @10min", value=player_stats.gold_diff_10, inline=True)

    elif isinstance(player_stats, JungleStats):
        embed.add_field(name="🌲 Jungle Proximity", value=f"{player_stats.jungle_proximity:.2f}%", inline=True)
        embed.add_field(name="🔪 First Blood", value="✅" if player_stats.first_blood else "❌", inline=True)
        embed.add_field(name="👹 Counter Jungling", value=f"{player_stats.counter_jungle:.2f}%", inline=True)

    elif isinstance(player_stats, MidStats):
        embed.add_field(name="📈 CSPM", value=f"{player_stats.cspm:.2f}", inline=True)
        embed.add_field(name="🔥 DPM", value=f"{player_stats.dpm:.2f}", inline=True)
        embed.add_field(name="🚶 Roaming %", value=f"{player_stats.roaming:.2f}%", inline=True)

    elif isinstance(player_stats, ADCStats):
        embed.add_field(name="📈 CSPM", value=f"{player_stats.cspm:.2f}", inline=True)
        embed.add_field(name="🔥 DPM", value=f"{player_stats.dpm:.2f}", inline=True)
        embed.add_field(name="⚡ Kill Conversion Rate", value=f"{player_stats.kill_conversion:.2f}", inline=True)

    elif isinstance(player_stats, SupportStats):
        embed.add_field(name="👀 Vision Score", value=player_stats.vision_score, inline=True)
        embed.add_field(name="🔗 Kill Participation", value=f"{player_stats.kill_participation:.2f}%", inline=True)
        embed.add_field(name="🎯 Objective Assist", value=player_stats.objective_assist, inline=True)

    embed.set_footer(text=f"Match ID: {match_id}")

    await ctx.send(embed=embed)

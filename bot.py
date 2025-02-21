import discord
from discord.ext import commands, tasks
from api.riot_api import get_puuid, get_match_history, get_match_details
from role_stats import TopStats, JungleStats, MidStats, ADCStats, SupportStats, PlayerStats, get_role_class
from model.users import Users
from config.config import DEFAULT_NUMBER_OF_GAMES, USERS_FILE
from discord import File
import pandas as pd
from model.files import Files

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize the Users manager with the path from config
users_manager = Users(USERS_FILE)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} è online!")

@bot.command()
async def register(ctx, game_name: str, tag: str, role: str):
    """Permette agli utenti di registrarsi con il proprio nome di gioco, tag e ruolo."""
    discord_id = str(ctx.author.id)
    users_manager.register_user(discord_id, game_name, tag, role)
    await ctx.send(f"✅ **{ctx.author.name}** registrato con successo come **{game_name}#{tag}** con ruolo **{role}**!")

@bot.command()
async def profile(ctx):
    """Mostra il profilo dell'utente corrente."""
    discord_id = str(ctx.author.id)
    # Assume that Users class has a to_string() method or similar for a pretty representation
    user_profile = users_manager.to_string(discord_id)
    if user_profile:
        await ctx.send(f"✅ Il profilo dell'utente **{ctx.author.name}** è **{user_profile}**")
    else:
        await ctx.send("❌ Profilo non trovato. Registrati usando `!register`.")

@bot.command()
async def stats(ctx, *args):
    """Mostra le statistiche dell'ultimo game di un giocatore. Se non viene fornito alcun parametro, mostra il proprio ultimo game."""
    if not args:
        discord_id = str(ctx.author.id)
        user = users_manager.get_user(discord_id)
        if user:
            game_name = user["game_name"]
            tag = user["tag"]
        else:
            await ctx.send("❌ Non sei registrato! Usa `!register NomeGiocatore Tag Ruolo` per registrarti.")
            return
    else:
        full_input = " ".join(args)
        if "#" not in full_input:
            await ctx.send("❌ Formato errato! Usa `Nome Giocatore#Tag`.")
            return
        game_name, tag = full_input.rsplit("#", 1)
        game_name, tag = game_name.strip(), tag.strip()

    await ctx.send(f"🔍 Cercando statistiche per **{game_name}#{tag}**...")
    puuid = get_puuid(game_name, tag)
    if not puuid:
        await ctx.send("❌ Giocatore non trovato!")
        return

    match_ids = get_match_history(puuid, count=1)
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

    player_stats = get_role_class(participant, team, game_duration)

    embed = discord.Embed(title=f"📊 Statistiche per {game_name} ({tag}) - {player_stats.champion}", color=0x00ff00)
    embed.add_field(name="🏅 Esito", value="✅ Vittoria" if player_stats.win else "❌ Sconfitta", inline=True)
    embed.add_field(name="⚔️ KDA", value=f"{player_stats.kills}/{player_stats.deaths}/{player_stats.assists}", inline=True)
    embed.add_field(name="🎮 Ruolo", value=player_stats.role, inline=True)

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

@bot.command()
async def dump(ctx, num_games: int = DEFAULT_NUMBER_OF_GAMES, match_type: str = "all"):
    """
    Fetch new match data, update the user's stats file with new matches, and keep the file sorted.
    The Excel file is named dynamically based on the user's Discord name.
    """
    if num_games < 1:
        await ctx.send("❌ Please provide a number between 1 and 20.")
        return

    valid_types = ["all", "ranked", "scrim"]
    if match_type.lower() not in valid_types:
        await ctx.send("❌ Invalid match type! Use `all`, `ranked`, or `scrim`.")
        return

    registered_players = users_manager.get_all_users()
    if not registered_players:
        await ctx.send("❌ Nessun giocatore registrato.")
        return

    # Create a dynamic file path based on the caller's Discord name
    discord_name = ctx.author.name.replace(" ", "_")
    file_path = f"../player_stats_{discord_name}.xlsx"

    try:
        files_handler = Files(file_path)  # Uses default required columns
    except Exception as e:
        await ctx.send(f"❌ Error loading Excel file: {e}")
        return

    new_rows = []
    fetched_matches = 0  

    for discord_id, player in registered_players.items():
        game_name = player["game_name"]
        tag = player["tag"]

        puuid = get_puuid(game_name, tag)
        if not puuid:
            continue  

        start = 0  
        while fetched_matches < num_games:
            match_ids = get_match_history(puuid, count=num_games, start=start)
            if not match_ids:
                break  

            for match_id in match_ids:
                if files_handler.match_exists(match_id):
                    continue  

                match_data = get_match_details(match_id)
                if not match_data or "info" not in match_data:
                    continue  

                participant = next((p for p in match_data["info"]["participants"] if p["puuid"] == puuid), None)
                if not participant:
                    continue  

                match_timestamp = match_data["info"]["gameStartTimestamp"]
                match_date = pd.to_datetime(match_timestamp, unit='ms').strftime('%m/%d/%Y')
                win_status = "Win" if participant["win"] else "Lose"
                champion = participant["championName"]
                kda = f'{participant["kills"]}/{participant["deaths"]}/{participant["assists"]}'
                kp = f'{round((participant["challenges"].get("killParticipation", 0) * 100), 1)}%' if "challenges" in participant else "N/A"
                vision_score = participant.get("visionScore", 0)
                vs_min = round(vision_score / (match_data["info"]["gameDuration"] / 60), 2)
                wards_placed = participant.get("wardsPlaced", 0)
                wards_destroyed = participant.get("wardsKilled", 0)
                control_wards = participant.get("visionWardsBoughtInGame", 0)
                game_duration = round(match_data["info"]["gameDuration"] / 60, 2)

                queue_type = match_data["info"].get("queueType", "Other")
                if queue_type not in ["Solo/Q", "Flex", "Scrim"]:
                    continue  

                new_rows.append([
                    queue_type, match_date, win_status, champion, kda, kp, 
                    vision_score, vs_min, wards_placed, wards_destroyed, 
                    control_wards, game_duration, match_id
                ])

                fetched_matches += 1  
                if fetched_matches >= num_games:
                    break  

            start += num_games  

    if not new_rows:
        await ctx.send("✅ No new matches found. The file remains unchanged.")
        return

    files_handler.add_rows(new_rows)
    files_handler.sort_by_date("Date")

    try:
        files_handler.save()
        await ctx.send(
            f"✅ Updated file with new {match_type} matches while keeping old data intact:",
            file=File(file_path)
        )
    except Exception as e:
        await ctx.send(f"❌ Error saving Excel file: {e}")

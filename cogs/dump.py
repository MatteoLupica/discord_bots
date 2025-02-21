import discord
from discord.ext import commands
import pandas as pd
from discord import File
from api.riot_api import get_puuid, get_match_history, get_match_details, RIOT_API_KEY, REGION
from config.config import DEFAULT_NUMBER_OF_GAMES
from model.users import Users
from model.files import Files

class DumpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_manager = Users()
    
    @commands.command()
    async def dump(self, ctx, num_games: int = DEFAULT_NUMBER_OF_GAMES, match_type: str = "all"):
        """
        Fetch new match data for all registered players, update the user's stats file 
        with new matches, and keep the file sorted.
        The Excel file is named dynamically based on the caller's Discord name.
        """
        if num_games < 1:
            await ctx.send("❌ Please provide a number between 1 and 20.")
            return

        valid_types = ["all", "ranked", "scrim"]
        if match_type.lower() not in valid_types:
            await ctx.send("❌ Invalid match type! Use `all`, `ranked`, or `scrim`.")
            return

        registered_players = self.users_manager.get_all_users()
        if not registered_players:
            await ctx.send("❌ Nessun giocatore registrato.")
            return

        # Create a dynamic file path based on the caller's Discord name
        discord_name = ctx.author.name.replace(" ", "_")
        file_path = f"../player_stats_{discord_name}.xlsx"

        try:
            files_handler = Files(file_path)  # Uses default required columns.
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
                    kp = (f'{round((participant["challenges"].get("killParticipation", 0) * 100), 1)}%'
                          if "challenges" in participant else "N/A")
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

    @commands.command()
    async def dump_full_stats(self, ctx, match_id: str):
        """
        Fetch match data, parse multiple tabs (Overview, Damage, Vision, Runes),
        and save them into one Excel file with multiple sheets.
        Usage: !dump_full_stats EUW1_1234567890
        """
        # Use the Riot API key and region from config.
        api_key = RIOT_API_KEY
        region = REGION
        match_data = get_match_details(match_id, api_key, region=region)
        if not match_data:
            await ctx.send("❌ Could not fetch match data from Riot API.")
            return

        # Parse each tab's data.
        overview_rows = parse_overview_tab(match_data)
        damage_rows = parse_damage_tab(match_data)
        vision_rows = parse_vision_tab(match_data)
        runes_rows = parse_runes_tab(match_data)
        
        df_overview = pd.DataFrame(overview_rows)
        df_damage = pd.DataFrame(damage_rows)
        df_vision = pd.DataFrame(vision_rows)
        df_runes = pd.DataFrame(runes_rows)
        
        file_path = f"match_{match_id}.xlsx"
        try:
            with pd.ExcelWriter(file_path) as writer:
                df_overview.to_excel(writer, sheet_name="Overview", index=False)
                df_damage.to_excel(writer, sheet_name="Damage", index=False)
                df_vision.to_excel(writer, sheet_name="Vision", index=False)
                df_runes.to_excel(writer, sheet_name="Runes", index=False)
        except Exception as e:
            await ctx.send(f"❌ Error saving Excel file: {e}")
            return
        
        await ctx.send(
            f"✅ Full stats for match `{match_id}` saved!",
            file=File(file_path)
        )

# Helper functions to parse full match data into tabs.
def parse_overview_tab(match_data):
    if not match_data or "info" not in match_data or "participants" not in match_data["info"]:
        return []
    rows = []
    for p in match_data["info"]["participants"]:
        row = {
            "SummonerName": p["summonerName"],
            "Champion": p["championName"],
            "Kills": p["kills"],
            "Deaths": p["deaths"],
            "Assists": p["assists"],
            "LargestMultiKill": p["largestMultiKill"],
            "Level": p["champLevel"],
            "GoldEarned": p["goldEarned"],
            "TotalMinionsKilled": p["totalMinionsKilled"],
            "NeutralMinionsKilled": p["neutralMinionsKilled"],
            "Item0": p["item0"],
            "Item1": p["item1"],
            "Item2": p["item2"],
            "Item3": p["item3"],
            "Item4": p["item4"],
            "Item5": p["item5"],
            "Item6": p["item6"],
            "KillParticipation": p["challenges"].get("killParticipation", None),
            "KDA": p["challenges"].get("kda", None),
        }
        rows.append(row)
    return rows

def parse_damage_tab(match_data):
    if not match_data or "info" not in match_data or "participants" not in match_data["info"]:
        return []
    rows = []
    for p in match_data["info"]["participants"]:
        row = {
            "SummonerName": p["summonerName"],
            "Champion": p["championName"],
            "TotalDamageToChamps": p["totalDamageDealtToChampions"],
            "PhysicalDamageToChamps": p["physicalDamageDealtToChampions"],
            "MagicDamageToChamps": p["magicDamageDealtToChampions"],
            "TrueDamageToChamps": p["trueDamageDealtToChampions"],
            "DamageDealtToTurrets": p["damageDealtToTurrets"],
            "DamageDealtToObjectives": p["damageDealtToObjectives"],
            "DamageSelfMitigated": p["damageSelfMitigated"],
            "SkillshotsHit": p["challenges"].get("skillshotsHit", None),
            "SkillshotsDodged": p["challenges"].get("skillshotsDodged", None),
        }
        rows.append(row)
    return rows

def parse_vision_tab(match_data):
    if not match_data or "info" not in match_data or "participants" not in match_data["info"]:
        return []
    rows = []
    for p in match_data["info"]["participants"]:
        row = {
            "SummonerName": p["summonerName"],
            "Champion": p["championName"],
            "VisionScore": p["visionScore"],
            "WardsPlaced": p["wardsPlaced"],
            "WardsKilled": p["wardsKilled"],
            "ControlWardsBought": p["visionWardsBoughtInGame"],
        }
        rows.append(row)
    return rows

def parse_runes_tab(match_data):
    if not match_data or "info" not in match_data or "participants" not in match_data["info"]:
        return []
    rows = []
    for p in match_data["info"]["participants"]:
        perks = p.get("perks", {})
        styles = perks.get("styles", [])
        primary_style = styles[0] if styles else {}
        secondary_style = styles[1] if len(styles) > 1 else {}
        row = {
            "SummonerName": p["summonerName"],
            "Champion": p["championName"],
            "PrimaryRunePath": primary_style.get("style", None),
            "PrimaryKeystone": (primary_style.get("selections", [{}])[0].get("perk", None)
                                if primary_style.get("selections") else None),
            "SecondaryRunePath": secondary_style.get("style", None) if secondary_style else None,
        }
        rows.append(row)
    return rows

async def setup(bot):
    await bot.add_cog(DumpCog(bot))

import discord
from discord.ext import commands
from model.users import Users
from utils.stats_parser import get_last_n_match_ids, get_match_stats
from utils.match_embed import build_match_embed

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_manager = Users()  # Uses default USERS_FILE from config.
    
    @commands.command()
    async def stats(self, ctx, *args):
        """
        Mostra le statistiche delle ultime partite.
        
        - Nessun argomento: usa il profilo registrato e mostra l'ultima partita.
        - Un argomento numerico (es. !stats 3): usa il profilo registrato e mostra le ultime 3 partite.
        - Un argomento "NomeGiocatore#Tag": usa quel summoner e mostra l'ultima partita.
        - Due argomenti ("NomeGiocatore#Tag" e un numero): usa quel summoner e mostra le ultime X partite.
        """
        num_matches = 1
        summoner_info = None

        if len(args) == 0:
            # Use registered player's info.
            discord_id = str(ctx.author.id)
            summoner_info = self.users_manager.get_user(discord_id)
            if not summoner_info:
                await ctx.send("❌ Non sei registrato! Usa `!register` per registrarti.")
                return
        elif len(args) == 1:
            arg = args[0]
            if arg.isdigit():
                num_matches = int(arg)
                if num_matches < 1:
                    await ctx.send("❌ Fornisci un numero positivo maggiore di 0.")
                    return
                discord_id = str(ctx.author.id)
                summoner_info = self.users_manager.get_user(discord_id)
                if not summoner_info:
                    await ctx.send("❌ Non sei registrato! Usa `!register` per registrarti.")
                    return
            elif "#" in arg:
                try:
                    game_name, tag = arg.rsplit("#", 1)
                    summoner_info = {"game_name": game_name.strip(), "tag": tag.strip()}
                except Exception:
                    await ctx.send("❌ Formato errato! Usa `NomeGiocatore#Tag`.")
                    return
            else:
                await ctx.send("❌ Argomento non valido. Fornisci un numero o un summoner nel formato `NomeGiocatore#Tag`.")
                return
        elif len(args) == 2:
            summ_arg, num_arg = args
            if "#" in summ_arg and num_arg.isdigit():
                try:
                    game_name, tag = summ_arg.rsplit("#", 1)
                    summoner_info = {"game_name": game_name.strip(), "tag": tag.strip()}
                    num_matches = int(num_arg)
                    if num_matches < 1:
                        await ctx.send("❌ Fornisci un numero positivo maggiore di 0.")
                        return
                except Exception:
                    await ctx.send("❌ Formato errato. Usa `NomeGiocatore#Tag <numero>`.")
                    return
            else:
                await ctx.send("❌ Formato errato. Usa `NomeGiocatore#Tag <numero>`.")
                return
        else:
            await ctx.send("❌ Numero di argomenti non valido. Usa 0, 1 o 2 argomenti.")
            return

        game_name = summoner_info["game_name"]
        tag = summoner_info["tag"]

        await ctx.send(f"🔍 Cercando le ultime {num_matches} partite per **{game_name}#{tag}**...")
        match_ids, error = get_last_n_match_ids(game_name, tag, num_matches)
        if error:
            await ctx.send(f"❌ {error}")
            return
        
        for match_id in match_ids:
            stats, error = get_match_stats(game_name, tag, match_id)
            if error:
                await ctx.send(f"⚠️ Errore in partita {match_id}: {error}")
                continue
            embed = build_match_embed(game_name, tag, match_id, stats)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(StatsCog(bot))

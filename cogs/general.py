import discord
from discord.ext import commands
from model.users import Users
from config.config import USERS_FILE

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_manager = Users(USERS_FILE)
    
    @commands.command()
    async def register(self, ctx, game_name: str, tag: str, role: str):
        """Permette agli utenti di registrarsi con il proprio nome di gioco, tag e ruolo."""
        discord_id = str(ctx.author.id)
        self.users_manager.register_user(discord_id, game_name, tag, role)
        await ctx.send(f"✅ **{ctx.author.name}** registrato con successo come **{game_name}#{tag}** con ruolo **{role}**!")
    
    @commands.command()
    async def profile(self, ctx):
        """Mostra il profilo dell'utente corrente."""
        discord_id = str(ctx.author.id)
        user_profile = self.users_manager.to_string(discord_id)
        if user_profile:
            await ctx.send(f"✅ Il profilo dell'utente **{ctx.author.name}** è **{user_profile}**")
        else:
            await ctx.send("❌ Profilo non trovato. Registrati usando `!register`.")

async def setup(bot):
    await bot.add_cog(General(bot))

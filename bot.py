import discord
from discord.ext import commands
from config.config import DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# List of cogs to load.
initial_extensions = ['cogs.general', 'cogs.stats', 'cogs.dump']

async def load_extensions():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"Loaded extension: {extension}")
        except Exception as e:
            print(f"Failed to load extension {extension}: {e}")

@bot.event
async def on_ready():
    await load_extensions()
    print("Registered commands:", [cmd.name for cmd in bot.commands])

# Directly use bot.run() to start the bot.
bot.run(DISCORD_TOKEN)

import logging
import os
import discord
import sqlite3
import datetime
import sys
# Import other Cogs here

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # Loads the .env file with the environment variables

intents = discord.Intents.default()  # Sets the default bot intents
intents.members = True  # Allows the bot to see members in a guild
intents.message_content = True  # Allows the bot to see message content
TOKEN = os.getenv("BOT_TOKEN")  # Sets the bot's token
COMMAND_PREFIX = "?"  # Sets the bots command prefix for non app commands
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)  # Defines bot
conn = sqlite3.connect("logging.db")  # Establishes a connection to the database
c = conn.cursor()  # Sets the cursor


# Load cogs function
async def load_cogs(bot):
    cogs = []  # Add cogs to be added here, once imported
    for cog in cogs:
        if not bot.get_cog(cog.__name__):
            try:
                await bot.load_extension(cog.__name__)
            except Exception as e:
                print(f"Failed to load cog {cog.__name__}: {e}")


# Bot ready event
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print("Ready!")


# Sync command to reload the app commands
@bot.command(pass_context=True, hidden=True)
@commands.is_owner()
async def sync(ctx):
    await ctx.bot.tree.sync()
    await ctx.send("Commands synced, you will need to reload Discord to see them")
    await ctx.message.delete()


# Adds a guild to the logging database when a new one is joined, for logging purposes
@bot.event
async def on_guild_join(guild):
    # Check if guild already exists in the database
    c.execute("SELECT * FROM guilds WHERE guild_id=?", (guild.id,))
    existing_guild = c.fetchone()
    if not existing_guild:
        # If guild is not in the database, add it
        c.execute("INSERT INTO guilds (guild.id) VALUES (?)", (guild.id,))
        conn.commit()
        print(f"Added {guild.name} to the database")
    else:
        print(f"{guild.name} is already in the database")


# Sets up the logging config and file format
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=f'log_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log',
                    filemode='a')  # Using 'a' mode to append to the file

# Create a StreamHandler for stdout
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(stdout_handler)

# Create a StreamHandler for stderr
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)
stderr_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(stderr_handler)


# Setup hook
@bot.event
async def on_connect():
    print("Bot is starting")
    await load_cogs(bot)
    print("Setup complete")


bot.run(TOKEN)

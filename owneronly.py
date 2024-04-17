import discord
import sqlite3
import logging

from discord.ext import commands

DATABASE_FILE = "logging.db"
COMMAND_PREFIX = "?"
OWNER_IDS = [1174000666012823565, 1108126443638116382]


def is_owner(ctx):
    return ctx.author.id in OWNER_IDS


class OwnerOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.cursor = self.conn.cursor()

    async def get_logging_channels(self, guild_id):  # Defines the function to load the logging channels
        query = "SELECT message_logs, member_logs, voice_logs, mod_logs, muterole, muterole_channel FROM guilds WHERE""guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            return result

    async def messagelogs(self, guild_id):  # Defines the function to load the logging channels
        query = "SELECT message_logs, member_logs, voice_logs, mod_logs, muterole, muterole_channel FROM guilds WHERE""guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            return result

    @commands.command()
    @commands.is_owner()
    async def list_cogs(self, ctx):
        loaded_cogs = "\n".join(self.bot.cogs.keys())
        await ctx.send(f"Loaded cogs: \n{loaded_cogs}")

    @commands.command(name="say", hidden=True)
    @commands.check(is_owner)
    async def say(self, ctx, *, message: str = None):
        guild = ctx.guild.id
        if message is None:
            await ctx.send("Please provide a message to repeat")
            return
        await ctx.send(message)
        await ctx.message.delete()
        print(f"Spirit said {message} in {guild}")

    @commands.command(name="sayall", hidden=True)
    @commands.check(is_owner)
    async def sayall(self, ctx, *, message: str = None):
        if message is None:
            await ctx.send("Please provide a message to send")
            return
        for guild in self.bot.guilds:
            logging_channel_id = self.messagelogs(guild.id)
            if logging_channel_id:
                logging_channel = guild.get_channel(logging_channel_id)
                if logging_channel:
                    await logging_channel.send(message)
                    await ctx.message.delete()
                    print(f"Spirit sent {message} in all guilds")

    @commands.command(name="dotstatus", hidden=True)
    @commands.check(is_owner)
    async def dotstatus(self, ctx, *, status: str):
        status = status.lower()
        presence_status = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.do_not_disturb,
            "offline": discord.Status.offline
        }.get(status)
        if presence_status is None:
            await ctx.send("Invalid status, please use one of the following: online, idle, dnd, offline")
            return
        await self.bot.change_presence(status=presence_status)
        await ctx.send(f"Bot status changed to {status.capitalize()}")
        await ctx.message.delete()
        print(f"Spirit changed bot status to {status.capitalize()}")


async def setup(bot):
    await bot.add_cog(OwnerOnly(bot))

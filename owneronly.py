import discord
import sqlite3
import logging

from discord.ext import commands, tasks

DATABASE_FILE = "logging.db"
COMMAND_PREFIX = "?"
OWNER_IDS = [1174000666012823565, 1108126443638116382]
logger = logging.getLogger(__name__)


def is_owner(ctx):
    return ctx.author.id in OWNER_IDS


class OwnerOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.cursor = self.conn.cursor()
        self.current_status = None
        self.refresh_status.start()

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
        guild = ctx.guild.name
        if message is None:
            await ctx.send("Please provide a message to repeat")
            return
        await ctx.send(message)
        await ctx.message.delete()
        logger.info(msg=f"Spirit said {message} in {guild}")

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
                    logger.info(msg=f"Spirit sent {message} in all guilds")

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
        logger.info(msg=f"Spirit changed bot status to {status.capitalize()}")

    @commands.command(name="nickname", hidden=True)
    @commands.check(is_owner)
    async def nickname(self, ctx, *, new_nickname: str):
        for guild in self.bot.guilds:
            try:
                await guild.me.edit(nick=new_nickname)
                await ctx.send(f"Bot nickname changed to {new_nickname}.")
            except Exception as e:
                await ctx.send(f"Failed to change bot nickname in {guild.name}: {e}.")

            await ctx.message.delete()
            logger.info(f"Spirit changed bot nickname to {new_nickname}.")

    @tasks.loop(hours=1)
    async def refresh_status(self):
        if self.current_status:
            await self.bot.change_presence(activity=discord.Game(name=self.current_status))
            logger.info(f"Bot status refreshed to {self.current_status}.")

    @commands.command(name="status", hidden=True)
    @commands.check(is_owner)
    async def status(self, ctx, *, new_status: str):
        self.current_status = new_status
        await self.bot.change_presence(activity=discord.Game(name=new_status))
        await ctx.send(f"Bot status changed to {new_status}.")
        await ctx.message.delete()
        logger.info(f"{ctx.author} changed bot status to Playing {new_status}.")

    @commands.command(name="glist", hidden=True)
    @commands.check(is_owner)
    async def glist(self, ctx):
        guilds = self.bot.guilds
        guild = ctx.guild
        content = ""
        for guild in guilds:
            line = f"{guild.name} - ID: {guild.id}\n"
            if len(content) + len(line) > 4000:
                await ctx.send(content)
                content = ""
            content += line
        if content:
            await ctx.send(content)
        await ctx.message.delete()
        logger.info(msg=f"Spirit ran command glist in {guild}")


async def setup(bot):
    await bot.add_cog(OwnerOnly(bot))

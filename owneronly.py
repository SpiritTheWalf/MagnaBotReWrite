import discord
import sqlite3
import logging
import os
import sys

from discord.ext import commands, tasks
from checks import is_dev, is_owner

DATABASE_FILE = "logging.db"
COMMAND_PREFIX = "?"
logger = logging.getLogger(__name__)


class OwnerOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.cursor = self.conn.cursor()
        self.current_status = None
        self.refresh_status.start()

    async def get_logging_channels(self, guild_id):  # Defines the function to load the logging channels
        query = ("SELECT message_logs, member_logs, voice_logs, mod_logs, muterole, muterole_channel FROM guilds WHERE "
                 "guild_id = ?")
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            return result

    async def messagelogs(self, guild_id):  # Defines the function to load the logging channels
        query = "SELECT message_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]

    @commands.command()
    @commands.is_owner()
    async def list_cogs(self, ctx):
        loaded_cogs = "\n".join(self.bot.cogs.keys())
        await ctx.send(f"Loaded cogs: \n{loaded_cogs}")

    @commands.command(name="say", hidden=True)
    @commands.check(is_owner)
    @commands.check(is_dev)
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
            logging_channel_id = await self.messagelogs(guild.id)
            print(logging_channel_id)
            if logging_channel_id:
                logging_channel = guild.get_channel(logging_channel_id)
                if logging_channel:
                    await logging_channel.send(message)
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

    @commands.command(name="ginfo", hidden=True)
    @commands.check(is_owner)
    async def ginfo(self, ctx, guild_id: int = None):
        if guild_id is None:
            guild_id = ctx.guild.id

        guild = self.bot.get_guild(guild_id)
        if guild is not None:
            owner = guild.owner
            total_members = guild.member_count
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            created_at = guild.created_at.strftime('%Y-%m-%d %H:%M:%S')
            bot_member = guild.get_member(self.bot.user.id)
            joined_at = bot_member.joined_at.strftime('%Y-%m-%d %H:%M:%S')

            embed = discord.Embed(title=f"Guild information - {guild.name}", color=discord.Color.blue())
            embed.add_field(name="Owner", value=f"{owner.name}", inline=False)
            embed.add_field(name="Total Members", value=total_members, inline=False)
            embed.add_field(name="Text Channels", value=text_channels, inline=False)
            embed.add_field(name="Voice Channels", value=voice_channels, inline=False)
            embed.add_field(name="Created At", value=created_at, inline=False)
            embed.add_field(name="Bot Joined At", value=joined_at, inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Guild not found")

        await ctx.message.delete()
        logger.info(f"Spirit ran command ginfo in {guild.name}")

    @commands.command(name="senddm", hidden=True)
    @commands.has_permissions(kick_members=True, administrator=True)
    async def senddm(self, ctx, user_id: int, *, message: str):
        user = self.bot.get_user(user_id)
        guild = ctx.guild
        author = ctx.author
        if user is not None:
            try:
                await user.send(f" - {message}\n\nSent by {author} from guild {guild}")
                await ctx.send("Done")
            except discord.HTTPException:
                await ctx.send(f"Failed to send a message to {user.name}.")
        else:
            await ctx.send("User not found.")

        logger.info(msg=f"{author} sent a message to {user} for reason {message} in guild {guild}")

    @commands.command(name='restart', hidden=True)
    @commands.check(is_owner)
    async def restart(self, ctx):
        await ctx.send('Restarting...')
        await self.bot.http.close()
        await self.bot.close()
        # Restart the bot process
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command(name="reload", hidden=True)
    @commands.check(is_owner)
    async def reload(self, ctx, cog_name: str):
        if f'cogs.{cog_name}' in self.bot.extensions:
            try:
                self.bot.reload_extension(f'cogs.{cog_name}')
                await ctx.send(f'{cog_name} reloaded successfully.')
            except commands.ExtensionError as e:
                await ctx.send(f'Failed to reload {cog_name}: {e}')
        else:
            try:
                self.bot.load_extension(f'cogs.{cog_name}')
                await ctx.send(f'{cog_name} loaded successfully.')
            except commands.ExtensionError as e:
                await ctx.send(f'Failed to load {cog_name}: {e}')

    @commands.command(name="cutie", hidden=True)
    @commands.check(is_owner)
    async def cutie(self, ctx):
        lycos = self.bot.get_user(int(952344652604903435))
        await ctx.send(f"{lycos.mention} is a cutie!")
        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(OwnerOnly(bot))

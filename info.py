import discord
import sqlite3

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Group, command
from discord.ext.commands import GroupCog
from version import VERSION

DATABASE_FILE = "logging.db"
COMMAND_PREFIX = "?"


class Info(GroupCog, group_name="info", group_description="Information commands about the bot"):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.cursor = self.conn.cursor()

    async def get_logging_channels(self, guild_id):  # Defines the function to load the logging channels
        query = ("SELECT message_logs, member_logs, voice_logs, mod_logs, muterole, muterole_channel FROM guilds WHERE "
                 "guild_id = ?")
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            return result

    @command(name="messagelogs", description="Prints the message logging channel")
    @commands.has_permissions(manage_guild=True)
    async def messagelogs(self, inter: discord.Interaction):
        guild_id = inter.guild_id
        query = "SELECT message_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            channel_id = result[0]
            channel = inter.guild.get_channel(channel_id)
            if channel:
                await inter.response.send_message(f"The message logging channel is {channel.mention}.", ephemeral=True)
            else:
                await inter.response.send_message("Message logging channel not set, please set it with `/setup "
                                                  "messagelogs`")
        else:
            await inter.response.send_message(
                "Message logging channel not set, please set it with `/setup messagelogs`")

    @command(name="memberlogs", description="Prints the member logging channel")
    @commands.has_permissions(manage_guild=True)
    async def memberlogs(self, inter: discord.Interaction):
        guild_id = inter.guild_id
        query = "SELECT member_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            channel_id = result[0]
            channel = inter.guild.get_channel(channel_id)
            if channel:
                await inter.response.send_message(f"The member logging channel is {channel.mention}.", ephemeral=True)
            else:
                await inter.response.send_message("The member logging channel is not set, please set it with `/setup "
                                                  "memberlogs`")
        else:
            await inter.response.send_message("The member logging channel is not set, please set it with `/setup "
                                              "memberlogs`")

    @command(name="voicelogs", description="Prints the voice logging channel")
    @commands.has_permissions(manage_guild=True)
    async def voicelogs(self, inter: discord.Interaction):
        guild_id = inter.guild_id
        query = "SELECT voice_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            channel_id = result[0]
            channel = inter.guild.get_channel(channel_id)
            if channel:
                await inter.response.send_message(f"The voice logging channel is {channel.mention}.", ephemeral=True)
            else:
                await inter.response.send_message("The voice logging channel is not set, please set it with `/setup "
                                                  "voicelogs`")
        else:
            await inter.response.send_message("The voice logging channel is not set, please set it with `/setup "
                                              "voicelogs`")

    @command(name="modlogs", description="Prints the moderation logging channel")
    @commands.has_permissions(manage_guild=True)
    async def modlogs(self, inter: discord.Interaction):
        guild_id = inter.guild_id
        query = "SELECT mod_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            channel_id = result[0]
            channel = inter.guild.get_channel(channel_id)
            if channel:
                await inter.response.send_message(f"The moderation logging channel is {channel.mention}.", ephemeral=True)
            else:
                await inter.response.send_message("The moderation logging channel is not set, please set it with "
                                                  "`/setup modlogs`")
        else:
            await inter.response.send_message("The moderation logging channel is not set, please set it with `/setup "
                                              "modlogs`")

    @command(name="ping", description="Get my ping to Discord")
    async def ping(self, inter: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await inter.response.send_message(f"Pong! My latency is {latency}ms.", ephemeral=True)

    @command(name="version", description="Prints the version of the bot")
    async def version(self, inter: discord.Interaction):
        await inter.response.send_message(f"The current version of MagnaBot is {VERSION}")


async def setup(bot):
    await bot.add_cog(Info(bot))

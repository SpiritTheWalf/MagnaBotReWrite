import discord
import sqlite3

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Group, command
from discord.ext.commands import GroupCog

DATABASE_FILE = "logging.db"
COMMAND_PREFIX = "?"

class Setup(GroupCog, group_name="setup", group_description="Bot setup commands"):
    def __init__(self, bot):
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.cursor = self.conn.cursor()

    async def get_logging_channels(self, guild_id):  # Defines the function to load the logging channels
        query = "SELECT message_logs, member_logs, voice_logs, mod_logs, muterole, muterole_channel FROM guilds WHERE""guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            return result
    @command(name="messagelogs", description="Sets the message logging channel")
    @commands.has_permissions(manage_guild=True)
    async def messagelogs(self, inter: discord.Interaction, channel: discord.TextChannel):
        guild_id = inter.guild_id
        channel_id = channel.id
        query = "UPDATE guilds SET message_logs = ? WHERE guild_id = ?"
        self.cursor.execute(query, (channel_id, guild_id))
        await inter.response.send_message(f"Message logging channel set to {channel.mention}.", ephemeral=True)
        self.conn.commit()

    @command(name="memberlogs", description="Sets the member logging channel")
    @commands.has_permissions(manage_guild=True)
    async def memberlogs(self, inter: discord.Interaction, channel: discord.TextChannel):
        guild_id = inter.guild_id
        channel_id = channel.id
        query = "UPDATE guilds SET member_logs = ? WHERE guild_id = ?"
        self.cursor.execute(query, (channel_id, guild_id))
        await inter.response.send_message(f"Member logging channel set to {channel.mention}.", ephemeral=True)
        self.conn.commit()

    @command(name="modlogs", description="Sets the moderation logging channel")
    @commands.has_permissions(manage_guild=True)
    async def modlogs(self, inter: discord.Interaction, channel: discord.TextChannel):
        guild_id = inter.guild_id
        channel_id = channel.id
        query = "UPDATE guilds SET mod_logs = ? WHERE guild_id = ?"
        self.cursor.execute(query, (channel_id, guild_id))
        await inter.response.send_message(f"Moderation logging channel set to {channel.mention}.", ephemeral=True)
        self.conn.commit()

    @command(name="voicelogs", description="Sets the voice logging channel")
    @commands.has_permissions(manage_guild=True)
    async def voicelogs(self, inter: discord.Interaction, channel: discord.TextChannel):
        guild_id = inter.guild_id
        channel_id = channel.id
        query = "UPDATE guilds SET voice_logs = ? WHERE guild_id = ?"
        self.cursor.execute(query, (channel_id, guild_id))
        await inter.response.send_message(f"Voice chat logging channel set to {channel.mention}.", ephemeral=True)
        self.conn.commit()

    async def update_database(self, guild_id, muterole_id, muterole_channel_id):
        query = "UPDATE guilds SET muterole = ?, muterole_channel = ? WHERE guild_id = ?"
        self.cursor.execute(query, (muterole_id, muterole_channel_id, guild_id))
        self.conn.commit()

    @command(name="muterole", description="Sets the muterole channel and description")
    @commands.has_permissions(manage_guild=True)
    async def muterole(self, inter: discord.Interaction, role: discord.Role, channel: discord.TextChannel):
        guild_id = inter.guild_id
        try:
            await self.update_database(guild_id, role.id, channel.id)

            channels = inter.guild.text_channels
            overwrite = discord.PermissionOverwrite()

            overwrite.send_messages = False
            overwrite.view_channel = False

            for c in channels:
                if c == channel:
                    continue

                await c.set_permissions(role, overwrite=overwrite, reason="Muterole Setup")

            await inter.response.send_message(f"{role.mention} has been muted in all channels except {channel.mention}.", ephemeral=True)
        except Exception as e:
            print(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Setup(bot))

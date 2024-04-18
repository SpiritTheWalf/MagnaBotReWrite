import sqlite3
import discord

from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone, timedelta

DATABASE_FILE = "logging.db"


def get_connection():
    return sqlite3.connect(DATABASE_FILE)


class LoggingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
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

    async def send_join_leave_logging_embed(self, guild, action, member, reason):
        guild_id = guild.id
        query = "SELECT member_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            channel_id = result[0]
            channel = guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title=f"Member {action}",
                    color=discord.Color.green() if action == "joined" else discord.Color.red()
                )
                if member.avatar:
                    embed.set_author(name=member.display_name, icon_url=member.avatar.url)
                else:
                    embed.set_author(name=member.display_name)

                embed.add_field(name="User", value=member.mention, inline=False)
                embed.add_field(name="User ID", value=member.id, inline=False)
                embed.add_field(name="Account creation date", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                                inline=False)
                embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                inline=False)
            if reason:
                embed.add_field(name="Reason", value=reason.capitalize(), inline=False)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        await self.send_join_leave_logging_embed(guild, "joined", member, reason=None)
        print(f"{member} joined a server")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        reason = None

        cutoff_time = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(seconds=30)

        async for entry in guild.audit_logs(action=discord.AuditLogAction.kick):
            if entry.target == member and entry.created_at > cutoff_time:
                reason = "Kicked"
                break

        await self.send_join_leave_logging_embed(guild, "left", member, reason)
        print(f"{member} left a server")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        guild_id = before.guild.id
        query = "SELECT message_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            channel_id = result[0]
            channel = before.guild.get_channel(channel_id)
            if channel:
                # Check if the message has content or attachments
                if before.content or len(before.attachments) > 0:
                    embed = discord.Embed(
                        title="Message Edited",
                        color=discord.Color.gold()
                    )
                    # Add fields for original and edited message content
                    if before.content:
                        embed.add_field(name="Before", value=before.content, inline=False)
                    if after.content:
                        embed.add_field(name="After", value=after.content, inline=False)
                    # Check for attachments (images, gifs) and include them in the embed
                    if before.attachments:
                        attachment_urls = [attachment.url for attachment in before.attachments]
                        embed.add_field(name="Attachments", value="\n".join(attachment_urls), inline=False)
                    # Add other information to the embed
                    embed.add_field(name="Author", value=before.author.mention, inline=False)
                    embed.add_field(name="Channel", value=before.channel.mention, inline=False)
                    embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                    inline=False)
                    await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild_id = member.guild.id
        query = "SELECT voice_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            channel_id = result[0]
            channel = member.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(color=discord.Color.blurple()
                                      )
                embed.add_field(name="User", value=member.mention, inline=False)
                embed.set_author(name=member.display_name, icon_url=member.avatar.url)

            if before.channel is None and after.channel is not None:
                embed.title = "Voice channel joined"
                embed.add_field(name="Channel", value=after.channel.mention, inline=False)
                embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                inline=False)
                await channel.send(embed=embed)

            elif before.channel is not None and after.channel is None:
                embed.title = "Voice channel left"
                embed.add_field(name="Channel", value=before.channel.mention, inline=False)
                embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                inline=False)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        guild_id = message.guild.id
        query = "SELECT message_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            channel_id = result[0]
            channel = message.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="Message Deleted",
                    color=discord.Color.red()
                )
                embed.add_field(name="Content", value=message.content, inline=False)
                embed.add_field(name="Author", value=message.author.mention, inline=False)
                embed.add_field(name="Channel", value=message.channel.mention, inline=False)
                embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                inline=False)
                await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(LoggingCog(bot))

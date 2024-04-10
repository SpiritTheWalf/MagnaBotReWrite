import discord
import sqlite3

from discord.ext import commands

DATABASE_FILE = "logging.db"
COMMAND_PREFIX = "?"


class botsetup(commands.Cog):  # Sets the name of our class, or cog
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect(DATABASE_FILE)  # Connect to the database
        self.cursor = self.conn.cursor()

    async def get_logging_channels(self, guild_id):  # Defines the function to load the logging channels
        query = "SELECT message_logs, member_logs, voice_logs, mod_logs, muterole, muterole_channel FROM guilds WHERE""guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            return result

    @commands.command(name="setmessagelogs", hidden=True)  # Defines the setmessagelogs command
    @commands.has_permissions(administrator=True)
    async def setmessagelogs(self, ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        channel_id = channel.id
        query = "UPDATE guilds SET message_logs = ? WHERE guild_id = ?"
        self.cursor.execute(query, (channel_id, guild_id))
        await ctx.send(f"Message logging channel set to {channel.mention}.")
        await ctx.message.delete()
        self.cursor.connection.commit()

    @commands.command(name="setmemberlogs", hidden=True)  # Defines the setmemberlogs command
    @commands.has_permissions(administrator=True)
    async def setmemberlogs(self, ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        channel_id = channel.id
        query = "UPDATE guilds SET member_logs = ? WHERE guild_id = ?"
        self.cursor.execute(query, (channel_id, guild_id))
        await ctx.send(f"Member logging channel set to {channel.mention}.")
        await ctx.message.delete()
        self.cursor.connection.commit()

    @commands.command(name="setvclogs", hidden=True)  # Defines the setvclogs command
    @commands.has_permissions(administrator=True)
    async def setvclogs(self, ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        channel_id = channel.id
        query = "UPDATE guilds SET voice_logs = ? WHERE guild_id = ?"
        self.cursor.execute(query, (channel_id, guild_id))
        await ctx.send(f"Voice logging channel set to {channel.mention}.")
        await ctx.message.delete()
        self.cursor.connection.commit()

    @commands.command(name="setmodlogs", hidden=True)  # Defines the setmodlogs command
    @commands.has_permissions(administrator=True)
    async def setmodlogs(self, ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        channel_id = channel.id
        query = "UPDATE guilds SET mod_logs = ? WHERE guild_id = ?"
        self.cursor.execute(query, (channel_id, guild_id))
        await ctx.send(f"Mod logging channel set to {channel.mention}.")
        await ctx.message.delete()
        self.cursor.connection.commit()

    @commands.command(name="getmessagelogs", hidden=True)  # Gets the messagelogs channel and prints it for the user
    @commands.has_permissions(administrator=True)
    async def getmessagelogs(self, ctx):
        guild_id = ctx.guild.id
        query = "SELECT message_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            channel_id = result[0]
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                await ctx.send(f"Message logging channel: {channel.mention}.")
            else:
                await ctx.send("Message logging channel not set.")
        else:
            await ctx.send("Message logging channel not set.")

        await ctx.message.delete()

    @commands.command(name="getmemberlogs", hidden=True)  # Gets the memberlogs channel and prints it for the user
    @commands.has_permissions(administrator=True)
    async def getmemberlogs(self, ctx):
        guild_id = ctx.guild.id
        query = "SELECT member_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            channel_id = result[0]
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                await ctx.send(f"Member logging channel: {channel.mention}.")
            else:
                await ctx.send("Member logging channel not set.")
        else:
            await ctx.send("Member logging channel not set.")

        await ctx.message.delete()

    @commands.command(name="getvclogs", hidden=True)  # Gets the vclogs channel and prints it for the user
    @commands.has_permissions(administrator=True)
    async def getvclogs(self, ctx):
        guild_id = ctx.guild.id
        query = "SELECT voice_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            channel_id = result[0]
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                await ctx.send(f"Voice logging channel: {channel.mention}.")
            else:
                await ctx.send("Voice logging channel not set.")
        else:
            await ctx.send("Voice logging channel not set.")

        await ctx.message.delete()

    @commands.command(name="getmodlogs", hidden=True)  # Gets the modlogs channel and prints it for the user
    @commands.has_permissions(administrator=True)
    async def getmodlogs(self, ctx):
        guild_id = ctx.guild.id
        query = "SELECT mod_logs FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()
        if result:
            channel_id = result[0]
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                await ctx.send(f"Mod logging channel: {channel.mention}.")
            else:
                await ctx.send("Mod logging channel not set.")
        else:
            await ctx.send("Mod logging channel not set.")

        await ctx.message.delete()

    async def update_database(self, guild_id, muterole_id, muterole_channel_id):  # Defines the update_database function.
        query = "UPDATE guilds SET muterole = ?, muterole_channel = ? WHERE guild_id = ?"
        self.cursor.execute(query, (muterole_id, muterole_channel_id, guild_id))
        self.cursor.connection.commit()

    @commands.command(name="muterole", hidden=True)  # Defines the command to set the muterole
    @commands.has_permissions(administrator=True)
    async def muterole(self, ctx, role: discord.Role, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        try:
            await self.update_database(guild_id, role.id, channel.id)

            channels = ctx.guild.text_channels
            overwrite = discord.PermissionOverwrite()

            overwrite.send_messages = False
            overwrite.view_channel = False

            for c in channels:
                if c == channel:
                    continue

                await c.set_permissions(role, overwrite=overwrite)

            await ctx.send(f"{role.mention} has been muted in all channels except {channel.mention}.")
        except Exception as e:
            print(f"An error occurred: {e}")

        await ctx.message.delete()

    @commands.command(name="getmuterole", hidden=True)
    @commands.has_permissions(administrator=True)
    async def getmuterole(self, ctx):
        guild_id = ctx.guild.id
        query = "SELECT muterole, muterole_channel FROM guilds WHERE guild_id = ?"
        self.cursor.execute(query, (guild_id,))
        result = self.cursor.fetchone()

        if result is None:
            await ctx.send("Muterole or muterole channel not saved")
            await ctx.message.delete()
            return

        role_id, channel_id = result

        muted_role = ctx.guild.get_role(role_id)
        mute_channel = ctx.guild.get_channel(channel_id)

        if mute_channel is None or muted_role is None:
            await ctx.send("Muterole or muted channel not set")
            await ctx.message.delete()
            return

        await ctx.send(f"The muterole is {muted_role.mention} and the muterole channel is {mute_channel.mention}")
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(botsetup(bot))

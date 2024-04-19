import discord
import sqlite3
import datetime
import asyncio
import logging

from discord.ext import commands
from discord import app_commands
from datetime import datetime
from discord import ui

DATABASE_FILE = "logging.db"
PUNISHMENT_DATABASE = "punishment_history.db"
COMMAND_PREFIX = "?"
logger = logging.getLogger(__name__)


class PaginatorView(discord.ui.View):
    def __init__(self, pages, channel, bot, user_id):
        super().__init__()
        self.pages = pages
        self.current_page = 0
        self.original_response = None
        self.channel = channel
        self.bot = bot
        self.user_id = user_id
        self.user_name = None  # Initialize user_name attribute

    async def show_page(self, inter: discord.Interaction = None, user_id: int = None):
        if self.user_name is None:  # Fetch username only if it's not fetched before
            try:
                user = await self.bot.fetch_user(self.user_id)
                self.user_name = user.name
            except discord.NotFound:
                self.user_name = "Unknown User"
                print(f"User not found for ID {self.user_id}")
            except discord.HTTPException as e:
                self.user_name = "Unknown User"
                print(f"Error fetching user {e}")

        title = f"Moderation history for {self.user_name} (Page {self.current_page + 1}/{len(self.pages)})"
        embed = discord.Embed(title=title, description=self.pages[self.current_page], color=0xff0000)

        # Send a new message with the embed
        try:
            self.original_response = await self.channel.send(embed=embed, view=self)
        except discord.Forbidden:
            print("Bot doesn't have permission to send messages in this channel.")

        # Acknowledge the interaction if it's not None and is an instance of discord.Interaction
        if isinstance(inter, discord.Interaction):
            try:
                await inter.response.send_message("Page sent.", ephemeral=True)
            except discord.HTTPException as e:
                print(f"Failed to acknowledge interaction: {e}")

        # Return the original response
        return self.original_response

    @discord.ui.button(label='◀️', style=discord.ButtonStyle.blurple)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.show_page(interaction)

    @discord.ui.button(label='▶️', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.show_page(interaction)


class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.conn = sqlite3.connect(PUNISHMENT_DATABASE)
        self.cursor = self.conn.cursor()

    def get_punishment_history(self, guild_id, user_id):
        conn = sqlite3.connect(PUNISHMENT_DATABASE)
        c = conn.cursor()
        c.execute("SELECT punishment_type, punishment_time, reason, punisher_id FROM punishments WHERE guild_id=? AND "
                  "user_id=?",
                  (guild_id, user_id))
        punishment_history = c.fetchall()
        conn.close()
        return punishment_history

    async def show_initial_page(self, inter: discord.Interaction, pages, user_id):
        view = PaginatorView(pages, inter.channel, self.bot, user_id)
        await view.show_page(inter)

        # Set the original response if inter is None
        if inter is None:
            self.original_response = view.original_response

    @app_commands.command(name="userhistory", description="Gets a user's punishment history")
    async def user_history(self, inter: discord.Interaction, user_id: str):
        user = self.bot.get_user(int(user_id))
        author = inter.user
        guild = inter.guild
        try:
            user_id = int(user_id)
        except ValueError:
            await inter.response.send_message("Please provide a valid user ID.")
            return

        guild_id = inter.guild.id
        try:
            history = self.get_punishment_history(guild_id, user_id)
        except Exception as e:
            print(f"Error fetching punishment history: {e}")
            await inter.response.send_message("An error occurred while fetching punishment history.")
            return

        if not history:
            await inter.response.send_message("No punishment history found for this user in this guild.")
            return

        logger.info(msg=f"{author} ran command userhistory on user {user} in guild {guild}")

        pages = []
        # Generate pages of punishment history
        page_size = 5
        for i in range(0, len(history), page_size):
            page = ""
            for punishment in history[i:i + page_size]:
                page += (f"**Type:** {punishment[0]}\n**Time:** {punishment[1]}\n**Reason:** {punishment[2]}\n"
                         f"**Moderator:** {punishment[3]}\n\n")
            pages.append(page)

        # Pass user_id to show_initial_page
        await self.show_initial_page(inter, pages, user_id)

    async def get_mod_logs_channel(self, guild_id):
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        query = "SELECT mod_logs FROM guilds WHERE guild_id = ?"
        c.execute(query, (guild_id,))
        result = c.fetchone()
        conn.close()
        if result:
            mod_logs_cid = result[0]
            return mod_logs_cid
        return None

    async def add_punishment(self, guild_id, user_id, punisher_id, punishment_type, punishment_time, reason):
        conn = sqlite3.connect(PUNISHMENT_DATABASE)
        c = conn.cursor()
        formatted_time = punishment_time.strftime("%Y-%m-%d %H:%M:%S")
        query = ("INSERT INTO punishments (guild_id, user_id, punisher_id, punishment_type, punishment_time, reason) "
                 "VALUES (?, ?, ?, ?, ?, ?)")
        c.execute(query, (guild_id, user_id, punisher_id, punishment_type, formatted_time, reason))
        conn.commit()
        conn.close()

    async def send_warning_embeds(self, channel, guild, issuer, user,
                                  reason):  # This is the embed format for the /warn command
        warning_embed = discord.Embed(title="User Warned", color=discord.Color.orange())
        warning_embed.add_field(name="User", value=user.display_name, inline=False)
        warning_embed.set_thumbnail(url=user.avatar.url)
        warning_embed.add_field(name="Issuer", value=issuer.display_name, inline=False)
        warning_embed.add_field(name="Reason", value=reason, inline=False)
        warning_embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                                inline=False)

        await channel.send(embed=warning_embed)

    async def send_kick_logging_embed(self, channel, guild, user, issuer, reason):
        embed = discord.Embed(title="User Kicked", color=discord.Color.red())
        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="Issuer", value=issuer.mention)
        embed.add_field(name="Reason", value=reason)
        embed.set_footer(text=f"Guild: {guild.name} | Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

        await channel.send(embed=embed)

    @app_commands.command(name="warn", description="Warn a user for violating rules")
    async def warn_command(self, inter: discord.Interaction, user: discord.Member, reason: str):
        guild = inter.guild
        if not guild:
            await inter.response.send_message("This command must be used in a server.")
            return

        # Check if the issuer has the "Kick Members" permission or is an administrator
        issuer = guild.get_member(inter.user.id)
        if not issuer:
            await inter.response.send_message("Failed to get issuer's information.")
            return

        if not issuer.guild_permissions.kick_members and not issuer.guild_permissions.administrator:
            await inter.response.send_message("You don't have permission to use this command.")
            return

        # Get the mod_logs channel ID
        mod_logs_cid = await self.get_mod_logs_channel(guild.id)
        if not mod_logs_cid:
            await inter.response.send_message("Moderation logs channel not found.")
            return

        # Get the mod_logs channel
        mod_logs_channel = guild.get_channel(mod_logs_cid)
        if not mod_logs_channel:
            await inter.response.send_message("Moderation logs channel not found.")
            return

        # Send warning embed to mod_logs channel
        await self.send_warning_embeds(mod_logs_channel, guild, issuer, user, reason)

        # Direct message the user being warned
        try:
            warning_embed = discord.Embed(title="You have been warned!", color=discord.Color.orange())
            warning_embed.set_thumbnail(url=user.avatar.url)
            warning_embed.add_field(name="Server", value=guild.name, inline=False)
            warning_embed.add_field(name="Issuer", value=issuer.display_name, inline=False)
            warning_embed.add_field(name="Reason", value=reason, inline=False)
            warning_embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                    inline=False)
            warning_embed.add_field(name="Guild", value=guild.name, inline=False)

            await user.send(embed=warning_embed)
        except discord.Forbidden:
            await inter.response.send_message("Failed to DM the user. Make sure they have DMs enabled.", ephemeral=True)

        # Add entry to punishment history database
        punisher_id = issuer.id
        punishment_time = datetime.utcnow()
        await self.add_punishment(guild.id, user.id, punisher_id, "warn", punishment_time, reason)

        await inter.response.send_message("User has been warned successfully.", ephemeral=True)
        author = inter.user
        guild = inter.guild
        logger.info(msg=f"{author} warned {user} in {guild} for {reason}")

    @app_commands.command(name="kick", description="Kick a user from the server")
    async def kick_command(self, inter: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        guild = inter.guild
        issuer = inter.user

        # Check if the issuer has the "Kick Members" permission or is an administrator
        if not issuer.guild_permissions.kick_members and not issuer.guild_permissions.administrator:
            await inter.response.send_message("You don't have permission to use this command.")
            return

        # Send DM to the kicked user
        try:
            kick_dm_embed = discord.Embed(title="You have been kicked from the server!", color=discord.Color.red())
            kick_dm_embed.set_thumbnail(url=user.avatar.url)
            kick_dm_embed.add_field(name="Server", value=guild.name, inline=False)
            kick_dm_embed.add_field(name="Issuer", value=issuer.display_name, inline=False)
            kick_dm_embed.add_field(name="Reason", value=reason, inline=False)
            kick_dm_embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                    inline=False)

            await user.send(embed=kick_dm_embed)
        except discord.Forbidden:
            await inter.response.send_message(
                "Failed to send a DM to the kicked user. Make sure they have DMs enabled.")

        # Kick the user
        try:
            await user.kick(reason=reason)
        except discord.Forbidden:
            await inter.response.send_message("I don't have permission to kick that user.")
            return

        # Add entry to punishment history database
        punisher_id = issuer.id
        punishment_time = datetime.utcnow()
        await self.add_punishment(guild.id, user.id, punisher_id, "kick", punishment_time, reason)

        # Get the default logging channel
        default_channel_id = await self.get_mod_logs_channel(guild.id)
        if not default_channel_id:
            await inter.response.send_message("Default logging channel not found.")
            return

        # Get the default logging channel
        default_channel = guild.get_channel(default_channel_id)
        if not default_channel:
            await inter.response.send_message("Default logging channel not found.")
            return

        # Send kick embed to default logging channel
        try:
            await self.send_kick_logging_embed(default_channel, guild, user, issuer, reason)
            await inter.response.send_message(f"{user.mention} has been kicked from the server for: {reason}",
                                              ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Failed to send embed to the default logging channel: {e}",
                                              ephemeral=True)

        author = inter.user
        guild = inter.guild
        logger.info(msg=f"{author} kicked {user} from {guild} for {reason}")

    async def send_ban_embed(self, channel, member, issuer, reason):  # Defines the structure of the embed
        ban_embed = discord.Embed(title="User Banned", color=discord.Color.red())
        ban_embed.set_thumbnail(url=member.avatar.url)
        ban_embed.add_field(name="User", value=user.display_name, inline=False)
        ban_embed.add_field(name="Issuer", value=issuer.display_name, inline=False)
        ban_embed.add_field(name="Reason", value=reason, inline=False)
        ban_embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                            inline=False)
        await channel.send(embed=ban_embed)

    @app_commands.command(name="ban", description="Ban a user from the server")
    async def ban_command(self, inter: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        issuer = inter.user
        guild = inter.guild

        # Send DM to the user
        try:
            ban_dm_embed = discord.Embed(title="You have been banned from the server!", color=discord.Color.red())
            ban_dm_embed.set_thumbnail(url=member.avatar.url)
            ban_dm_embed.add_field(name="Server", value=guild.name, inline=False)
            ban_dm_embed.add_field(name="Issuer", value=issuer.display_name, inline=False)  # Change to display_name
            ban_dm_embed.add_field(name="Reason", value=reason, inline=False)
            ban_dm_embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                   inline=False)
            await member.send(embed=ban_dm_embed)
        except discord.Forbidden:
            await inter.response.send_message("Failed to send a DM to the user. Make sure they have DMs enabled.")

        # Ban the user
        try:
            await guild.ban(member, reason=reason)
        except discord.Forbidden:
            await inter.response.send_message("I don't have permission to ban that user.")
            return

        # Add ban details to the database
        punisher_id = issuer.id
        ban_time = datetime.utcnow()
        await self.add_punishment(guild.id, member.id, punisher_id, "ban", ban_time, reason)

        # Get the default logging channel
        default_channel_id = await self.get_mod_logs_channel(guild.id)
        if not default_channel_id:
            await inter.response.send_message("Default logging channel not found.")
            return

        # Get the default logging channel
        default_channel = guild.get_channel(default_channel_id)
        if not default_channel:
            await inter.response.send_message("Default logging channel not found.")
            return

        # Send ban embed to default logging channel
        await self.send_ban_embed(default_channel, member, issuer, reason)

        await inter.response.send_message(f"{member.mention} has been banned from the server for: {reason}")

        author = inter.user
        guild = inter.guild
        logger.info(msg=f"{author} banned {member} from {guild} for {reason}")

    async def send_unban_embed(self, channel, user, issuer):  # Defines the embed for the unban command
        unban_embed = discord.Embed(title="User Unbanned", color=discord.Color.green())
        unban_embed.set_thumbnail(url=user.avatar.url)
        unban_embed.add_field(name="User", value=user.display_name, inline=False)
        unban_embed.add_field(name="Issuer", value=issuer.display_name, inline=False)
        unban_embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                              inline=False)
        await channel.send(embed=unban_embed)

    @app_commands.command(name="unban", description="Unban a user from the server")
    async def unban_command(self, inter: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        issuer = inter.user
        guild = inter.guild

        # Check if the issuer has the "Ban Members" permission or is an administrator
        if not issuer.guild_permissions.ban_members and not issuer.guild_permissions.administrator:
            await inter.response.send_message("You don't have permission to use this command.")
            return

        # Convert user_id to integer
        try:
            user_id = int(user_id)
        except ValueError:
            await inter.response.send_message("Invalid user ID provided.")
            return

        # Convert user_id to discord.User object
        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            await inter.response.send_message("User not found.")
            return

        # Unban the user
        try:
            await guild.unban(user, reason=reason)
        except discord.Forbidden:
            await inter.response.send_message("I don't have permission to unban that user.")
            return

        # Get the default logging channel
        default_channel_id = await self.get_mod_logs_channel(guild.id)
        if not default_channel_id:
            await inter.response.send_message("Default logging channel not found.")
            return

        # Get the default logging channel
        default_channel = guild.get_channel(default_channel_id)
        if not default_channel:
            await inter.response.send_message("Default logging channel not found.")
            return

        # Add unban details to the database
        punisher_id = issuer.id
        unban_time = datetime.utcnow()
        await self.add_punishment(guild.id, user.id, punisher_id, "unban", unban_time, reason)

        # Send unban embed to default logging channel
        await self.send_unban_embed(default_channel, user, issuer)

        await inter.response.send_message(f"{user.mention} has been unbanned from the server.")

        author = inter.user
        guild = inter.guild
        logger.info(msg=f"{author} unbanned {user} from {guild} for {reason}")

    async def get_mute_role(self, guild_id):
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        query = "SELECT muterole FROM guilds WHERE guild_id = ?"
        c.execute(query, (guild_id,))
        result = c.fetchone()
        conn.close()  # Close the connection after usage
        return result[0] if result else None

    @app_commands.command(name="mute", description="Give the muted role to a specified user.")
    @commands.has_permissions(moderate_members=True, administrator=True)
    async def mute(self, inter: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        guild = inter.guild

        role_id = await self.get_mute_role(guild.id)

        if role_id is None:
            await inter.response.send_message("Muted role not found.")
            return

        muted_role = guild.get_role(role_id)

        if muted_role is None:
            await inter.response.send_message("Muted role not found.")
            return

        await member.add_roles(muted_role)
        await inter.response.send_message(f"{member.mention} has been muted.")

        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

        # Send a DM to the user with an embed
        dm_embed = discord.Embed(
            title="You have been muted!",
            description=f"You have been muted in {guild.name}",
            color=discord.Color.orange()
        )
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        dm_embed.set_author(name=f"Action by {inter.user}", icon_url=inter.user.display_avatar)
        dm_embed.set_thumbnail(url=avatar_url)
        dm_embed.add_field(name="Guild", value=guild.name, inline=False)
        await member.send(embed=dm_embed)

        # Log the action
        mod_log_channel_id = await self.get_mod_logs_channel(guild.id)
        if mod_log_channel_id:
            mod_log_channel = guild.get_channel(mod_log_channel_id)
            if mod_log_channel:
                mod_log_embed = discord.Embed(
                    title="Mute",
                    description=f"{member.mention} has been muted.",
                    color=discord.Color.orange()
                )
                mod_log_embed.set_author(name=f"Action by {inter.user}", icon_url=inter.user.display_avatar)
                mod_log_embed.set_thumbnail(url=avatar_url)
                mod_log_embed.add_field(name="Guild", value=guild.name, inline=False)
                mod_log_embed.add_field(name="Reason", value=reason, inline=False)
                await mod_log_channel.send(embed=mod_log_embed)
            else:
                print(f"Mod logging channel not found in {guild.name}.")
        else:
            print(f"Default logging channel not found.")

        # Log the punishment
        punisher_id = inter.user.id
        unban_time = datetime.utcnow()
        await self.add_punishment(guild.id, member.id, punisher_id, "mute", unban_time, reason)

        author = inter.user
        guild = inter.guild
        logger.info(msg=f"{author} muted {user} from {guild} for {reason}")

    @app_commands.command(name="unmute", description="Unmutes a user.")
    @commands.has_permissions(moderate_members=True, administrator=True)
    async def mute(self, inter: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        guild = inter.guild

        role_id = await self.get_mute_role(guild.id)

        if role_id is None:
            await inter.response.send_message("Muted role not found.")
            return

        muted_role = guild.get_role(role_id)

        if muted_role is None:
            await inter.response.send_message("Muted role not found.")
            return

        await member.remove_roles(muted_role)
        await inter.response.send_message(f"{member.mention} has been ummuted.")

        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

        # Send a DM to the user with an embed
        dm_embed = discord.Embed(
            title="You have been unmuted!",
            description=f"You have been unmuted in {guild.name}",
            color=discord.Color.orange()
        )
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        dm_embed.set_author(name=f"Action by {inter.user}", icon_url=inter.user.display_avatar)
        dm_embed.set_thumbnail(url=avatar_url)
        dm_embed.add_field(name="Guild", value=guild.name, inline=False)
        await member.send(embed=dm_embed)

        # Log the action
        mod_log_channel_id = await self.get_mod_logs_channel(guild.id)
        if mod_log_channel_id:
            mod_log_channel = guild.get_channel(mod_log_channel_id)
            if mod_log_channel:
                mod_log_embed = discord.Embed(
                    title="Unmute",
                    description=f"{member.mention} has been unmuted.",
                    color=discord.Color.orange()
                )
                mod_log_embed.set_author(name=f"Action by {inter.user}", icon_url=inter.user.display_avatar)
                mod_log_embed.set_thumbnail(url=avatar_url)
                mod_log_embed.add_field(name="Guild", value=guild.name, inline=False)
                mod_log_embed.add_field(name="Reason", value=reason, inline=False)
                await mod_log_channel.send(embed=mod_log_embed)
            else:
                print(f"Mod logging channel not found in {guild.name}.")
        else:
            print(f"Default logging channel not found.")

        # Log the punishment
        punisher_id = inter.user.id
        unban_time = datetime.utcnow()
        await self.add_punishment(guild.id, member.id, punisher_id, "unmute", unban_time, reason)

        author = inter.user
        guild = inter.guild
        logger.info(msg=f"{author} unmuted {user} from {guild} for {reason}")


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))

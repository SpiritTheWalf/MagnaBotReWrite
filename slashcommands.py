import discord

from datetime import datetime
from pytz import all_timezones, timezone
from discord.ext import commands
from discord import app_commands

class SlashCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="support", description="Prints an invite to the support server")
    async def support(self, inter: discord.Interaction):
        await inter.response.send_message("<https://discord.gg/qVTRbZ3j3z>")

    @app_commands.command(name="roleadd", description="Adds a role to a user")
    async  def roleadd(self, inter: discord.Interaction, user: discord.Member, role: discord.Role):
        if inter.user.guild_permissions.manage_roles or inter.user.guild_permissions.administrator:
            await user.add_roles(role)
            await inter.response.send_message(f"Added {role} to {user}.")
        else:
            await inter.response.send_message("You do not have permission to use this command.")

    @app_commands.command(name="roleremove", description="Removes a role from a user")
    async  def roleremove(self, inter: discord.Interaction, user: discord.Member, role: discord.Role):
        if inter.user.guild_permissions.manage_roles or inter.user.guild_permissions.administrator:
            await user.remove_roles(role)
            await inter.response.send_message(f"Removed {role} from {user}.")
        else:
            await inter.response.send_message("You do not have permission to use this command.")

    @app_commands.command(name="rolequery", description="Check if a user has a particular role")
    async def rolequery(self, inter: discord.Interaction, user: discord.Member, role: discord.Role):
        if role in user.roles:
            await inter.response.send_message(f"{user.display_name} has the role {role.name}.")
        else:
            await inter.response.send_message(f"{user.display_name} does not have the role {role.name}.")

    @app_commands.command(name="getuserroles", description="List all roles a user has")
    async def getuserroles(self, inter: discord.Interaction, user: discord.Member):
        role_list = ", ".join([role.name for role in user.roles])
        await inter.response.send_message(f"{user.display_name} has the following roles: {role_list}")

    @app_commands.command(name="echo", description="Repeats what the user says")
    async def echo(self, inter: discord.Interaction, message: str):
        """
        Repeats what the user says.
        """
        await inter.response.send_message(message)

async def setup(bot):
    await bot.add_cog(SlashCog(bot))
import discord

from discord.app_commands import Group, command
from discord.ext.commands import GroupCog


class Utility(GroupCog, group_name="utility", group_description="utility commands"):
    def __init__(self, bot):
        self.bot = bot

    @command(name="support", description="Prints a link to the support server")
    async def support(self, inter: discord.Interaction):
        await inter.response.send_message("The support server is <https://discord.gg/qVTRbZ3j3z>")

    @command(name="rolequery", description="Checks to see if a user has a particular role")
    async def rolequery(self, inter: discord.Interaction, user: discord.Member, role: discord.Role):
        if role in user.roles:
            await inter.response.send_message(f"{user.display_name} has the role {role.name}")
        else:
            await inter.response.send_message(f"{user.display_name} does not have the role {role.name}")

    @command(name="echo", description="Echoes the user's input")
    async def echo(self, inter: discord.Interaction, message: str):
        await inter.response.send_message(message)


async def setup(bot):
    await bot.add_cog(Utility(bot))

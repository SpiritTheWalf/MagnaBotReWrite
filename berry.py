import discord

from discord import app_commands
from discord.ext import commands


class Berry(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="berry", description="It's a berry! I know someone who might like this!")
    async def berry(self, inter: discord.Interaction):
        await inter.response.send_message("You have a berry! 🍓 What will you do with it?")


async def setup(bot):
    await bot.add_cog(Berry(bot))

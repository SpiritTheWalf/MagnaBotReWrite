import discord

from discord import app_commands
from discord.ext import commands


class Gay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if "gay" in message.content.lower():
            try:
                await message.add_reaction("🌈")
            except discord.Forbidden:
                print("Unable to add reaction - insufficient permissions.")


async def setup(bot):
    await bot.add_cog(Gay(bot))

import os
import discord
import requests

from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

load_dotenv()
API_KEY = os.getenv("SHERI_API_KEY")


class Sheri(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_url = "https://sheri.bot/api"
        self.api_key = API_KEY

    @commands.command(name="endpoints")
    async def endpoints(self, ctx):
        if ctx.channel.is_nsfw():
            await ctx.send("# SFW ENDPOINTS\n\nbday, belly_rub, blep, bonk, boop, bunny, cat, cry, cuddle, deer, fox, "
                           "goat, hold, horse, hug, husky, kiss, lick, lion, mur, nature, pat, paws, pig, plane, "
                           "pokemon, proposal, sfwsergal, shiba, snek, snep, tiger, turkey, turtle, wolves, "
                           "yeen\n\n\n\n# NSFW ENDPOINTS\n\n69, anal, bang, bisexual, boob, boobwank, booty, "
                           "christmas, cumflation, dick, dick_wank, dickmilk, dickorgy, dp, fbound, fcreampie, "
                           "femboypresentation, finger, fpresentation, frot, fseduce, fsolo, ftease, futabang, gay, "
                           "gay_bang, gif, handjob, herm_bang, impregnated, jockstraps, lesbian, lesbian_bang, lick, "
                           "maws, mbound, mcreampie, mpresentation, mseduce, msolo, mtease, nboop, nbrony, nbulge, "
                           "ncomics, ncuddle, ndeer, nfelkins, nfemboy, nfox, nfuta, ngroup, nhold, nhug, nhusky, "
                           "nkiss, nleopard, nlick, npanther, npat, npokemon, nprotogen, nscalies, nsfwselfies, "
                           "nsolo, nspank, ntease, ntrap, pawjob, pawlick, pegging_bang, petplay, pregnant, "
                           "pussy, pussy_eating, ride, rimjob selfsuck, sfwsergal, straight_bang, suck, "
                           "tentacles, toys, videos, vore, vorefanal, voreforal, vorefunbirth, voremanal, voremcock, "
                           "voremoral, yiff")
        else:
            await ctx.send("SFW ENDPOINTS\n\nbday, belly_rub, blep, bonk, boop, bunny, cat, cry, cuddle, deer, fox, "
                           "goat, hold, horse, hug, husky, kiss, lick, lion, mur, nature, pat, paws, pig, plane, "
                           "pokemon, proposal, rpanda, sfwsergal, shiba, snek, snep, tiger, turkey, turtle, wolves, "
                           "yeen")

    @app_commands.command(name="media", description="Pulls an image from a specified endpoint")
    async def media(self, inter: discord.Interaction, endpoint: str):

        nsfw_endpoints = ["69", "anal", "bang", "bisexual", "boob",
                          "boobwank",
                          "booty", "christmas", "cumflation", "cuntboy", "cuntboy_bang", "dick",
                          "dick_wank",
                          "dickmilk", "dickorgy", "dp", "fbound", "fcreampie", "femboypresentation", "finger",
                          "fpresentation",
                          "frot", "fseduce", "fsolo", "ftease", "futabang", "gay", "gay_bang", "gif",
                          "handjob", "herm_bang",
                          "impregnated", "jockstraps", "lesbian", "lesbian_bang", "maws", "mbound",
                          "mcreampie", "mpresentation",
                          "mseduce", "msolo", "mtease", "nboop", "nbrony", "nbulge", "ncomics", "ncuddle",
                          "ndeer", "nfelkins",
                          "nfemboy", "nfox", "nfuta", "ngroup", "nhold", "nhug", "nhusky", "nkiss",
                          "nleopard", "nlick", "npanther",
                          "npat", "npokemon", "nprotogen", "nscalies", "nsfwselfies", "nsolo", "nspank",
                          "ntease", "ntrap", "pawjob",
                          "pawlick", "paws", "pegging_bang", "petplay", "pregnant", "pussy", "pussy_eating",
                          "ride", "rimjob", "rpanda", "selfsuck", "straight_bang", "suck",
                          "tentacles", "toys", "videos", "vore", "voreforal", "vorefunbirth", "voremanal",
                          "voremcock", "voremoral", "yiff"]
        if endpoint in nsfw_endpoints and not inter.channel.is_nsfw():
            await inter.response.send_message("The endpoint is NSFW and can only be used in NSFW channels.")
            return

        api_url = f"https://sheri.bot/api/{endpoint}"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "User-Agent": "MagnaBot/3.0 (Python Requests) Coded by SpiritTheWalf"
        }
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            image_url = response.json().get("url")
            if image_url:
                embed = discord.Embed()
                embed.set_image(url=image_url)
                embed.set_footer(text="Powered by the Sheri API")
                embed.add_field(name="", value=f"[🌐 Direct URL to image]({image_url})", inline=True)
                await inter.response.send_message(embed=embed)
            else:
                await inter.response.send_message("Error: No valid image in that endpoint, please try again later.")
        else:
            await inter.response.send_message(
                f"Error: Could not fetch image from {api_url}. Status code: {response.status_code}")

    @media.autocomplete("endpoint")
    async def endpoint_autocomplete(self, inter: discord.Interaction, current: str) -> list[
        app_commands.Choice[str]]:
        try:
            if inter.channel.is_nsfw():
                all_choices = ["bday", "belly_rub", "blep", "bonk", "boop", "bunny", "cat", "cry", "cuddle", "deer",
                               "fox",
                               "goat", "hold", "horse", "hug", "husky", "kiss", "lick", "lion", "mur", "nature", "pat",
                               "paws",
                               "pig", "plane", "pokemon", "proposal", "rpanda", "sfwsergal", "shiba", "snek", "snep",
                               "tiger", "turkey", "turtle", "wolves", "yeen", "69", "anal", "bang", "bisexual", "boob",
                               "boobwank",
                               "booty", "christmas", "cumflation", "cuntboy", "cuntboy_bang", "dick",
                               "dick_wank",
                               "dickmilk", "dickorgy", "dp", "fbound", "fcreampie", "femboypresentation", "finger",
                               "fpresentation",
                               "frot", "fseduce", "fsolo", "ftease", "futabang", "gay", "gay_bang", "gif",
                               "handjob", "herm_bang",
                               "impregnated", "jockstraps", "lesbian", "lesbian_bang", "maws", "mbound",
                               "mcreampie", "mpresentation",
                               "mseduce", "msolo", "mtease", "nboop", "nbrony", "nbulge", "ncomics", "ncuddle",
                               "ndeer", "nfelkins",
                               "nfemboy", "nfox", "nfuta", "ngroup", "nhold", "nhug", "nhusky", "nkiss",
                               "nleopard", "nlick", "npanther",
                               "npat", "npokemon", "nprotogen", "nscalies", "nsfwselfies", "nsolo", "nspank",
                               "ntease", "ntrap", "pawjob",
                               "pawlick", "paws", "pegging_bang", "petplay", "pregnant", "pussy", "pussy_eating",
                               "ride", "rimjob", "rpanda", "selfsuck", "straight_bang", "suck",
                               "tentacles", "toys", "videos", "vore", "voreforal", "vorefunbirth", "voremanal",
                               "voremcock", "voremoral", "yiff"]
            else:
                all_choices = ["bday", "belly_rub", "blep", "bonk", "boop", "bunny", "cat", "cry", "cuddle", "deer",
                               "fox",
                               "goat", "hold", "horse", "hug", "husky", "kiss", "lick", "lion", "mur", "nature",
                               "pat", "paws",
                               "pig", "plane", "pokemon", "proposal", "rpanda", "sfwsergal", "shiba", "snek",
                               "snep", "tiger",
                               "turkey", "turtle", "wolves", "yeen"]

            return [app_commands.Choice(name=endpoint, value=endpoint)
                    for endpoint in all_choices if current.lower() in endpoint.lower()][:25]
        except Exception as e:
            await inter.response.send_message(f"An error occurred: {e}")
            print(f"An error occurred: {e}")


async def setup(bot):
    await bot.add_cog(Sheri(bot))

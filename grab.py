import discord

from discord.ext import commands
from checks import is_owner


class Grab(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.check(is_owner)
    async def grab(self, ctx):
        await ctx.send("Available grab sheets:\nkit\nspirit\nyoung_magna\nyirra\nbrini\nvakur\nmagna\nshy")
        await ctx.message.delete()

    @grab.command(name="kit", hidden=True)
    @commands.check(is_owner)
    async def kit(self, ctx):
        embed = discord.Embed(title="Kit the Femboy Fox")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1222375500861935637/1222376416855982143/shyguy.png?ex"
                "=6646c540&is=664573c0&hm=d37d9bbdb0aff4bb98cb6ca44ba02e0d4334a3587a09f905be422acdbf8d34a5&")
        embed.add_field(name="Age", value="21", inline=False)
        embed.add_field(name="Species", value="Fox", inline=False)
        embed.add_field(name="Pronouns", value="He/Him", inline=False)
        embed.add_field(name="About Me",
                        value="Heya! I'm Kit! I was Shy's first 'fursona', and even though I am not always out, "
                              "I am still here, just mention me and ill pop in and say hi",
                        inline=False)
        embed.set_footer(text="Last Updated on 05/16/2024")
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @grab.command(name="spirit", hidden=True)
    @commands.check(is_owner)
    async def spirit(self, ctx):
        embed = discord.Embed(title="Spirit", description="Also known as Spirit Wolf, SpiritTheWalf")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1222375524278472705/1239399432080855041"
                                "/SpiritSweater.png?ex=6646bcab&is=66456b2b&hm"
                                "=a67f9f57136ebc16714d5ec6628cc792f98c5162d85b9b1fa17eeabe834c8ad3&")
        embed.add_field(name="Age", value="20", inline=False)
        embed.add_field(name="Species", value="Wolf", inline=False)
        embed.add_field(name="Pronouns", value="She/Her", inline=False)
        embed.add_field(name="About Me", value="Hoi there! I'm Spirit! I am the main... controller of Shy (It's "
                                               "complicated xD)\nMost of the time you'll be talking to me, "
                                               "but the others are there, just ask for them xD", inline=False)
        embed.set_footer(text="Last Updated on 05/16/2024")
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @grab.command(name="young_magna", hidden=True)
    @commands.check(is_owner)
    async def young_magna(self, ctx):
        embed = discord.Embed(title="Magna the teen ProtoDerg", description="Also known as Young Magna")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1240625403920650300/1240625583713423501/21"
                                ".jpg?ex=66473e1c&is=6645ec9c&hm"
                                "=8a93c1436229443e3eaf1ef9078bc8465d504aeb06610aca249b2a3ecde2a9b1&")
        embed.add_field(name="Age", value="16", inline=False)
        embed.add_field(name="Species", value="ProtoDerg", inline=False)
        embed.add_field(name="Pronouns", value="He/Him", inline=False)
        embed.add_field(name="About Me", value="Born under uncertain circumstances, not much is known about Young "
                                               "Magna, but his skills and magic strength are remarkably strong, "
                                               "one is advised to keep their guard up around Young Magna", inline=False)
        embed.set_footer(text="Last Updated on 05/16/2024")
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @grab.command(name="yirra", hidden=True)
    @commands.check(is_owner)
    async def yirra(self, ctx):
        embed = discord.Embed(title="Yirra")
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/1222375538681708555/1222376516013395968/snepproto.jpg?ex"
                "=6646c558&is=664573d8&hm=315baa48b66e8a13612db626c9739bd9a4fe5b208e26a6a0e4784db1787e96b5&=&format"
                "=webp&width=450&height=676")
        embed.add_field(name="Age", value="26", inline=False)
        embed.add_field(name="Species", value="CyberSnep", inline=False)
        embed.add_field(name="Pronouns", value="She/Her", inline=False)
        embed.add_field(name="About Me",
                        value="Yirra is a hunter by nature, often aggressive if she does not know you, but once she "
                              "does she is very calm and cool, just steer clear when she does get annoyed, "
                              "as it is not good for anyone involved",
                        inline=False)
        embed.set_footer(text="Last Updated on 05/26/2024")
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @grab.command(name="brini", hidden=True)
    @commands.check(is_owner)
    async def brini(self, ctx):
        embed = discord.Embed(title="Brini")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1222375415415574598/1240629996041670706/1.jpg"
                                "?ex=664d30f8&is=664bdf78&hm"
                                "=6692b9cabd1efe57a425f8849976003eb1279576583eb02573961a2cd837712b&")
        embed.add_field(name="Species", value="Panda", inline=False)
        embed.add_field(name="age", value="31", inline=False)
        embed.add_field(name="Pronouns", value="She/Her", inline=False)
        embed.add_field(name="About Me", value="Brini is an artist in more ways than one, from simple drawing to "
                                               "music and many other things besides.", inline=False)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @grab.command(name="vakur", hidden=True)
    @commands.check(is_owner)
    async def vakur(self, ctx):
        embed = discord.Embed(title="Vakur", description="Also known as Lt Cdr Vakur")
        embed.set_thumbnail(url="https://cdn.tupperbox.app/pfp/1174000666012823565/o55ldyXoXPSKPe3i.webp")
        embed.add_field(name="Species", value="Hyena", inline=False)
        embed.add_field(name="Age", value="37", inline=False)
        embed.add_field(name="Pronouns", value="He/Him", inline=False)
        embed.add_field(name="About me", value="Vakur is a strong willed and serious individual, always there when "
                                               "you need him. His navy skills are also used frequently.", inline=False)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @grab.command(name="magna", hidden=True)
    @commands.check(is_owner)
    async def magna(self, ctx):
        embed = discord.Embed(title="Magna")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1222375513172217856/1222375837551296512"
                                "/synth3.jpg?ex=664d5c36&is=664c0ab6&hm"
                                "=e0e15ba4298c2185918a85210f7c276dc9b651f2348f62aeb0db969912d9e35b&=&format=webp"
                                "&width=450&height=676")
        embed.add_field(name="Species", value="Synth", inline=False)
        embed.add_field(name="Age", value="30", inline=False)
        embed.add_field(name="Pronouns", value="She/Her", inline=False)
        embed.add_field(name="About Me", value="Having evolved from a protogen into a synth a few months back, "
                                               "she is still learning about her new body and what it can do, "
                                               "approach with caution", inline=False)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @grab.command(name="shy", hidden=True)
    @commands.check(is_owner)
    async def shy(self, ctx):
        embed = discord.Embed(title="Shy", description="Also known as Shy Guy, TheRealShyGuy")
        embed.set_thumbnail(url="https://cdn.tupperbox.app/pfp/1174000666012823565/xWRbNFqoFPEJiReH.webp")
        embed.add_field(name="Species", value="Human", inline=False)
        embed.add_field(name="Age", value="19", inline=False)
        embed.add_field(name="Pronouns", value="He/Him", inline=False)
        embed.add_field(name="About Me", value="Shy is the human behind all this, content to let Spirit do most of "
                                               "the talking, you won't see him around often, but make sure to say Hi "
                                               "if you do", inline=False)
        await ctx.send(embed=embed)
        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(Grab(bot))

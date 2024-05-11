import discord
import sqlite3

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Group, command
from discord.ext.commands import GroupCog

DATABASE_FILE = "economy.db"
COMMAND_PREFIX = "?"
OWNER_IDS = [1174000666012823565, 1108126443638116382]
DEV_IDS = [952344652604903435, 1174000666012823565]


def is_owner(ctx):
    return ctx.author.id in OWNER_IDS


def is_dev(ctx):
    return ctx.message.author.id in DEV_IDS


class Economy(GroupCog, group_name="economy", group_description="Economy related commands"):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.cursor = self.conn.cursor()

    @command(name="balance", description="Displays how many coins you have")
    async def balance(self, inter: discord.Interaction, user: discord.User = None):
        if user is None:
            user = inter.user

        query = "SELECT coins FROM members WHERE user_id = ?"
        self.cursor.execute(query, (user.id,))
        result = self.cursor.fetchone()

        if result:
            coins = result[0]
            await inter.response.send_message(f"{user.display_name} has {coins} coins!")
        else:
            self.cursor.execute("INSERT INTO members (user_id, coins) VALUES (?, ?)", (user.id, 100))
            self.conn.commit()
            await inter.response.send_message(f"{user.display_name} has been added to the database and given 100 "
                                              f"coins as a starting gift! How lucky!")

    @command(name="givecoins", description="Gives coins to a user, staff only")
    @commands.check(is_owner)
    @commands.check(is_dev)
    async def givecoins(self, inter: discord.Interaction, user: discord.User, amount: int):
        if amount <= 0:
            await inter.response.send_message("Please provide an amount larger than 0.")
            return
        self.cursor.execute("SELECT coins FROM members WHERE user_id = ?", (user.id,))
        result = self.cursor.fetchone()
        if result:
            receiver_coins = result[0]
            new_coins = receiver_coins + amount
            self.cursor.execute("UPDATE members SET coins = ? WHERE user_id = ?", (new_coins, user.id,))
        else:
            self.cursor.execute("INSERT INTO members (user_id, coins) VALUES (?, ?)", (int(user.id), amount,))

        self.conn.commit()
        await inter.response.send_message(f"{user.display_name} has been given {amount} coins! Lucky!")

    @command(name="rmcoins", description="Removes coins from a user, staff only")
    @commands.check(is_owner)
    @commands.check(is_dev)
    async def rmcoins(self, inter: discord.Interaction, user: discord.User, amount: int):
        if amount <= 0:
            await inter.response.send_message("Please provide an amount larger than 0.")
            return
        self.cursor.execute("SELECT coins FROM members WHERE user_id = ?", (user.id,))
        result = self.cursor.fetchone()
        if result:
            receiver_coins = result[0]
            new_coins = receiver_coins - amount
            self.cursor.execute("UPDATE members SET coins = ? WHERE user_id = ?", (new_coins, user.id,))
        else:
            self.cursor.execute("INSERT INTO members (user_id, coins) VALUES (?, ?)", (int(user.id), amount,))

        self.conn.commit()
        await inter.response.send_message(f"{amount} coins have been removed from {user.display_name}'s balance. They "
                                          f"must have been a naughty fur...")

    @command(name="buy", description="Buy items from the economy shop")
    @app_commands.choices(
        item=[
            app_commands.Choice(name="LGBT Heart 🌈❤️", value="heart"),
            app_commands.Choice(name="Item 2", value="item2"),
            app_commands.Choice(name="Item 3", value="item3")
        ]
    )
    async def buy(self, inter: discord.Interaction, item: str, quantity: int = 1):
        user = inter.user
        item_prices = {
            "heart": 100,
            "item2": 20,
            "item3": 30
            # Add more items and their prices as needed
        }

        if quantity <= 0:
            await inter.response.send_message("Please provide a greater quantity than 0")
            return

        total_cost = item_prices[item.lower()] * quantity

        query = "SELECT coins FROM members WHERE user_id = ?"
        self.cursor.execute(query, (user.id,))
        result = self.cursor.fetchone()
        user_coins = result[0]


        if user_coins < total_cost:
            await inter.response.send_message(f"You do not have enough coins to make this purchase.")
            return

        self.cursor.execute("SELECT coins FROM members WHERE user_id = ?", (user.id,))
        result = self.cursor.fetchone()
        if result:
            balance = result[0]
            new_coins = balance - total_cost
            self.cursor.execute("UPDATE members SET coins = ? WHERE user_id = ?", (new_coins, user.id,))
        else:
            self.cursor.execute("INSERT INTO members (user_id, coins) VALUES (?, ?)", (int(user.id), amount,))

        self.conn.commit()
        await inter.response.send_message(f"Successfully bought {quantity} {item} for {total_cost} coins.")


async def setup(bot):
    await bot.add_cog(Economy(bot))

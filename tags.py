import discord
from discord.ext import commands
import sqlite3

from checks import is_owner


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.initialize_database()

    def initialize_database(self):
        with sqlite3.connect('tags.db') as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    name TEXT PRIMARY KEY,
                    content TEXT
                )
            ''')
            conn.commit()

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, name: str = None):
        """Query a tag"""
        if name is None:
            await ctx.send("Please provide a tag name.")
        else:
            with sqlite3.connect('tags.db') as conn:
                c = conn.cursor()
                c.execute('SELECT content FROM tags WHERE name = ?', (name,))
                row = c.fetchone()
                if row:
                    await ctx.send(row[0])
                else:
                    await ctx.send(f"Tag '{name}' not found.")

    @tag.command()
    @commands.check(is_owner)
    async def create(self, ctx, name: str, *, content: str):
        """Create a new tag"""
        with sqlite3.connect('tags.db') as conn:
            c = conn.cursor()
            try:
                c.execute('INSERT INTO tags (name, content) VALUES (?, ?)', (name, content))
                conn.commit()
                await ctx.send(f"Tag '{name}' created.")
            except sqlite3.IntegrityError:
                await ctx.send(f"Tag '{name}' already exists.")

    @tag.command()
    @commands.check(is_owner)
    async def remove(self, ctx, name: str):
        """Remove a tag"""
        with sqlite3.connect('tags.db') as conn:
            c = conn.cursor()
            c.execute('DELETE FROM tags WHERE name = ?', (name,))
            conn.commit()
            if c.rowcount:
                await ctx.send(f"Tag '{name}' removed.")
            else:
                await ctx.send(f"Tag '{name}' not found.")

    @tag.command()
    @commands.check(is_owner)
    async def list(self, ctx):
        """List all tags, or the first 25 if there are too many"""
        with sqlite3.connect('tags.db') as conn:
            c = conn.cursor()
            c.execute('SELECT name FROM tags')
            rows = c.fetchall()
            if rows:
                tag_list = [row[0] for row in rows]
                if len(tag_list) > 25:
                    tag_list = tag_list[:25]
                await ctx.send(f"Tags:\n" + "\n".join(tag_list))
            else:
                await ctx.send("No tags found.")


async def setup(bot):
    await bot.add_cog(Tags(bot))

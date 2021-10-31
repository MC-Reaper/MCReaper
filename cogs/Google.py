# Google cog by Doz
# ---------------------------------------------------------------------------
import discord, asyncio
from discord import Member
from discord.ext.commands import Bot
from discord.ext import commands
from googlesearch import search
# ---------------------------------------------------------------------------
class Google(commands.Cog):
    """Commands for Google"""
    
    def __init__(self, bot):
        self.bot = bot

    # TODO: Make this customizable.
    @commands.command(aliases=['gsearch', 'glookup'])
    async def google(self, ctx, *, query=None):

        if query == None:
            return await ctx.send("`USAGE: gsearch <query>`\nLooks up for the first 5 results.\nTry `gsearch ducks`.")

        results = '\n '.join(str(x) for x in search(query, tld="com", num=5, stop=5, pause=2))

        if results == '':
            results = ":x: I couldn't search for that!"
        await ctx.reply(results)
# ---------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Google(bot))
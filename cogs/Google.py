# Google cog by Doz
# ---------------------------------------------------------------------------
import discord, asyncio
from discord import Member, Webhook, RequestsWebhookAdapter
from discord.ext.commands import Bot
from discord.ext import commands
from googlesearch import search
# ---------------------------------------------------------------------------
# Webhook logging
errorlogs_webhook = Webhook.partial(746156734019665929, "i88z41TM5VLxuqnbIdM7EjW1SiaK8GkSUu0H3fOTLBZ9RDQmcOG0xoz6P5j1IafoU1t5",\
 adapter=RequestsWebhookAdapter())
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

        try:
            results = '\n '.join(str(x) for x in search(query, tld="com", num=5, stop=5, pause=2))
        except Exception as e:
            await ctx.send('An unknown error has occured, sent error log to HQ.')
            return errorlogs_webhook.send(f"```[ERROR] CMD|GSEARCH: {e}```")

        if results == '':
            results = "Couldn't search for that!"
        await ctx.send(results)
# ---------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Google(bot))
# Google cog by Doz
# ---------------------------------------------------------------------------
import discord, asyncio, random
from discord import Member, Webhook, RequestsWebhookAdapter
from discord.ext.commands import Bot
from discord.ext import commands
from googletrans import Translator
from googlesearch import search
# ---------------------------------------------------------------------------
# Webhook logging
errorlogs_webhook = Webhook.partial(746156734019665929, "i88z41TM5VLxuqnbIdM7EjW1SiaK8GkSUu0H3fOTLBZ9RDQmcOG0xoz6P5j1IafoU1t5",\
 adapter=RequestsWebhookAdapter()) #errorlogs in HQ
# ---------------------------------------------------------------------------
def RandomColour():
    """Generates random Colours"""

    randColour = discord.Colour(random.randint(0x000000, 0xFFFFFF))
    return randColour

class Google(commands.Cog):
    """Commands for Google"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gghelp(self, ctx):
        """Help page for Google"""

        embed =discord.Embed(title="GOOGLE HELP", description="Commands for google search & translate.", colour=discord.Colour.red())
        embed.add_field(name="COMMANDS", value="`gsearch <query>` searches for the first 5 results.\n- `tl <text>` translates a language to English.\n- `tlc <language> <text>` Auto Detect to specified language.", inline=False)
        await ctx.send(embed=embed)

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

    @commands.command(aliases=['trans', 'tl'])
    async def translate(self, ctx, *, txt=None):
        """Translates a language to English."""

        await ctx.send("Currently Broken because Google keeps messing with us.")

        """
        if txt == None:
            return await ctx.send("`USAGE: tl <text>`")

        try:
            translator = Translator()
            translation = translator.translate(txt, dest='en')
            lang = translator.detect(txt)
        except Exception as e:
            if ("'NoneType' object has no attribute 'group'" in str(e)):
                return await ctx.send('You expect me to translate some alien language?')
            else:
                return errorlogs_webhook.send(f"```[ERROR] CMD|TL: {e}```")

        em = discord.Embed(title='Translator', colour=RandomColour())
        em.add_field(name='Original Text:', value=txt, inline=False)
        em.add_field(name='Translated Text:', value=translation.text, inline=False)
        em.set_footer(text=f'Detected Language: {lang.lang}')

        return await ctx.send(embed=em)
        """

    @commands.command(aliases=['tlc'])
    async def translatec(self, ctx, lg=None, *, txt=None):
        """Translates a language to Another language."""

        await ctx.send("Currently Broken because Google keeps messing with us.")

        """
        if lg == None:
            return await ctx.send("`USAGE: tlc <language> <text>`")

        if txt == None:
            return await ctx.send("`USAGE: tlc <language> <text>`")

        try:
            translator = Translator()
            translation = translator.translate(txt, dest=lg)
        except Exception as e:
            if 'invalid destination language' in str(e):
                await ctx.send(f"{lg} is not a language!")
            else:
                await ctx.send('An unknown error has occured, sent error log to HQ.')
                return errorlogs_webhook.send(f"```[ERROR] CMD|TLC: {e}```")

        em = discord.Embed(title='Translator', colour=RandomColour())
        em.add_field(name='Original Text:', value=txt, inline=False)
        em.add_field(name='Translated Text:', value=translation.text, inline=False)
        em.set_footer(text=f'Language used: {lg}')

        return await ctx.send(embed=em)
        """

# ---------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Google(bot))
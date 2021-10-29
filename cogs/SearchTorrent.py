# SearchTorrent cog by Doz, Using we-get python module: https://github.com/rachmadaniHaryono/we-get
# ---------------------------------------------------------------------------
import discord, asyncio, requests, json
from we_get.core.we_get import WG
from discord import Member, File
from discord.ext.commands import Bot
from discord.ext import commands
from os import remove
# ---------------------------------------------------------------------------
we_get = WG()
# ---------------------------------------------------------------------------
class SearchTorrent(commands.Cog):
    """Search for a torret based on keywords then return info about the torrents"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['searchtorrent', 'findtorrent'])
    async def fetchtorrent(self, ctx, *, keyword : str = None):
        """Searches for torrents given a keyword."""

        async with ctx.typing():

            if keyword == None:
                return await ctx.send("Um, Please type what you want to search please.\n`fetchtorrent <keyword>`")
        
            smsg = await ctx.send("```Please wait...```")

            we_get.parse_arguments(['--search', keyword, '--target', '1337x'])
            resultDict = we_get.start(api_mode=True)

            count = 0
            for result in resultDict:
                count += 1
                
            if (count == 0):
                return await smsg.edit(content=f"I couldn't find results for {keyword}!")

            await smsg.edit(content=f"```Obtained {count} results for {keyword}```")

            for result in resultDict:

                resultEmbed = discord.Embed(
                    title='Torrent Fetcher',
                    description=f"**__Magnet Link__**\n\n```{resultDict[result]['link']}```"
                    )

                resultEmbed.add_field(name='File Name', value=result, inline=False)
                resultEmbed.add_field(name='Seeds', value=resultDict[result]['seeds'], inline=True)
                resultEmbed.add_field(name='Leeches', value=resultDict[result]['leeches'], inline=True)
                resultEmbed.set_footer(text="Powered by we-get")

                await ctx.reply(embed=resultEmbed)

# ---------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(SearchTorrent(bot))
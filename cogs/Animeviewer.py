# Animeviewer cog by Doz
# ---------------------------------------------------------------------------
import discord, asyncio, requests, json
from discord import Member
from discord.ext.commands import Bot
from discord.ext import commands
# ---------------------------------------------------------------------------
class Animeviewer(commands.Cog):
    """Fetch anime stream links"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def animesearch(self, ctx, *, keyword : str = None):
        """ Search for anime """

        async with ctx.typing():

            if keyword == None:
                return await ctx.send(
                    "Hey there, you did not use this command corrently, here is the usage!\n\n",
                    "```animesearch <keyword>\nkeyword is the name of the anime. Be as specific as possible to get the closest results. Once you get a result, use animeview [episode#] <animetitle> (default is episode 1) to get the video link.```")
        
            smsg = await ctx.send("```Please wait...```")


            try:

                from anime_downloader.sites import get_anime_class

                AKisa = get_anime_class('animekisa')
                search = AKisa.search(keyword)

                from anime_downloader.sites.animekisa import AnimeKisa
                anime = AnimeKisa(search[0].url)

                em = discord.Embed(title='Anime Search')

                em.add_field(name='Keyword', value=keyword, inline=False)
                em.add_field(name='Anime Title', value=anime, inline=False)
                em.add_field(name='No. of Episodes', value=len(anime), inline=False)
                em.add_field(name='Stream link to Episode 1', value=f'[First Episode]({anime[0].source().stream_url})')

                await smsg.edit(content=None, embed=em)

            except Exception as e:
                if 'list index out of range' in str(e):
                    await smsg.edit(content="I couldn't find that! Please check your spelling, make sure the anime actually exists and be more specific.\nE.g: ```animesearch Boku No Hero Academia 4``` *4* is the season.")
                else:
                    raise Exception

    @commands.command()
    async def animeview(self, ctx, episodenum: int = 1, *, keyword : str = None):
        """ Search for anime """

        async with ctx.typing():
        
            smsg = await ctx.send("```Please wait...```")

            try:

                from anime_downloader.sites import get_anime_class

                AKisa = get_anime_class('animekisa')
                search = AKisa.search(keyword)

                from anime_downloader.sites.animekisa import AnimeKisa
                anime = AnimeKisa(search[0].url)

                em = discord.Embed(title='Anime Search')

                em.add_field(name='Keyword', value=keyword, inline=False)
                em.add_field(name='Anime Title', value=anime, inline=False)
                em.add_field(name='No. of Episodes', value=len(anime), inline=False)
                em.add_field(name=f'Stream link to Episode {episodenum}', value=f'[Link]({anime[episodenum - 1].source().stream_url})')

                await smsg.edit(content=None, embed=em)

            except Exception as e:
                if 'list index out of range' in str(e):
                    await smsg.edit(content="I couldn't find that! Please check your spelling, make sure the anime actually exists and be more specific.\nE.g: ```animeview 25 Boku No Hero Academia 4```")
                elif 'No episode found with index' in str(e):
                    await smsg.edit(content="I couldn't find that! Please check your spelling, make sure the anime actually exists and be more specific.\nE.g: ```animeview 25 Boku No Hero Academia 4```")
                else:
                    raise NameError(e)

# ---------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Animeviewer(bot))

# GBan cog by Doz
# ---------------------------------------------------------------------------
import discord, asyncio, random, json, pymongo, os
from pymongo import MongoClient
from discord import Member
from discord.ext.commands import Bot, has_permissions, CheckFailure, MemberConverter
from discord.ext import commands
# ---------------------------------------------------------------------------
# Load configuration file
with open('config.json') as a:
    config = json.load(a)
# ---------------------------------------------------------------------------
BAN_GIF = config.get("ban_gif")
DOZ_DISCORD = 'Doz#1040'
BOT_OWNER_ID = int(config.get("bot_owner_id"))
# ---------------------------------------------------------------------------
# MongoDB Configuration
MONGOSRV = os.environ['MONGOSRV']
cluster = MongoClient(MONGOSRV)
db = cluster["mcreaper"]
# Collections
gbanned_users_c = db["gbanned_users"]
sudo_users_c = db["sudo_users"]
# ---------------------------------------------------------------------------
# Checks
async def SUDOER_CHECK(ctx):
    """A check to ensure nobody but SUDOERS can run these commands."""
    query = {"_id": ctx.author.id}
    if ctx.message.author.id == BOT_OWNER_ID:
        return True
    elif (sudo_users_c.count_documents(query) == 1):
        return True
    else:
        return False
# ---------------------------------------------------------------------------
class Gban(commands.Cog):
    """Commands for managing Federation bans"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def gbhelp(self, ctx):
        """Help page for Federation Ban"""

        embed=discord.Embed(title="Federation Ban Help", description="These are the commands that can be used by bot owners to keep your servers in check!", colour=discord.Colour.red())
        embed.add_field(name="Commands", value="- `gban <user> [reason]` Bans a user from every server I share with.\n- `ungban <user> [reason]` removes the user from the GBAN database.", inline=False)
        await ctx.send(embed=embed)

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def gban(self, ctx, txt = None, *, reason = None):
        """Federation Ban"""

        await ctx.message.delete()

        if txt == None:
            return await ctx.send("`USAGE: gban <user> [reason]`")
        if reason == None:
            reason = "No reason provided."

        for a in txt:
            if (a.isnumeric()) == True:
                try:
                    user = await self.bot.fetch_user(txt)
                except:
                    pass
            else:
                try:
                    converter = MemberConverter()
                    user = await converter.convert(ctx, txt)
                except:
                    return await ctx.send(f"{ctx.author.mention}, I can't find that user!")

        if user.id == ctx.author.id:
            return await ctx.send(f"Are you trying to ban yourself from the federation {ctx.author.mention}?")
        if user.id == BOT_OWNER_ID:
            return await ctx.send(f"Silly {ctx.author.mention}! You can't ban the Bot Owner!")

        async with ctx.typing():

            query = {"_id": user.id}
            try:
                if (gbanned_users_c.count_documents(query) == 0):
                    post = {"_id": user.id, "user": user.name+'#'+user.discriminator ,"reason": reason}
                    gbanned_users_c.insert_one(post)
                else:
                    gbanned_users_c.update_one({"_id":user.id}, {"$set":{"user":user.name+'#'+user.discriminator,"reason":reason}})
                    await ctx.send(f'{user} ({user.id}) was already gbanned! New reason set!: {gbanned_users_c.find_one(query)["reason"]}')
            except Exception as e:
                await ctx.send('Aborted operation due to an error on the database.')
                return print(f'>>> Failed to add user to GBAN DATABSE!\nEXCEPTION: {e}')

            initbanmsg = await ctx.send(f">>> Initiating GBAN for {user}...")
        
            for guild in self.bot.guilds:
                try:
                    await guild.ban(user, reason=reason)
                    print(f'gbanned {user} from {guild.name} successfully!')
                except Exception as e:
                    print(f'Failed to gban {user} from {guild.name}!\nDetails:\n{e}')

            try:
                embed = discord.Embed(title='Federation Ban Notice', description=f'You were banned from the federation by {ctx.author}', colour=discord.Colour.red())
                embed.add_field(name='Reason:', value=reason, inline=False)
                embed.add_field(name='Federation BAN?', value=f'If you think this ban was unjustified please contact the bot owner {DOZ_DISCORD} ({BOT_OWNER_ID}) to get unbanned!')
                embed.set_footer(text=f'Banned by {ctx.message.author.name}', icon_url=ctx.message.author.avatar_url_as(static_format='png'))
                embed.set_image(url=BAN_GIF)
                await user.send(embed=embed)
            except:
                print(f'>>> Federation Ban message not sent to {user} ({user.id})')
                pass


            try:
                embed = discord.Embed(title='Federation Ban Notice', description=f'{user} ({user.id}) has been banned from the federation by {ctx.message.author}', colour=discord.Colour.red())
                embed.add_field(name='Reason:', value=f'{reason}', inline=False)
                embed.set_footer(text=f'Banned by {ctx.message.author.name}', icon_url=ctx.message.author.avatar_url_as(static_format='png'))
                await ctx.send(embed=embed)
                await initbanmsg.delete()
                print(f'{user} ({user.id}) has been banned from the federation by {ctx.message.author}\nReason{reason}')
            except Exception as e:
                await ctx.send('An unknown error has occured, sent error log to HQ.')
                print(f"[ERROR] CMD|GBAN: {e}")

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def ungban(self, ctx, txt = None, *, reason = None):
        """
        Removes a user from the GBAN database
        However, the server must unban that person after he/she is ungbanned.
        """

        await ctx.message.delete()

        if txt == None:
            return await ctx.send("`USAGE: ungban <user> [reason]`")
        if reason == None:
            reason = "No reason provided."

        for a in txt:
            if (a.isnumeric()) == True:
                try:
                    user = await self.bot.fetch_user(txt)
                except:
                    pass
            else:
                try:
                    converter = MemberConverter()
                    user = await converter.convert(ctx, txt)
                except:
                    return await ctx.send(f"{ctx.author.mention}, I can't find that user!")

        async with ctx.typing():

            query = {"_id": user.id}
            if (gbanned_users_c.count_documents(query) == 1):
                try:
                    embed = discord.Embed(title='Federation Unban Notice', description=f'{user} has been unbanned by {ctx.message.author} ({ctx.message.author.id})', colour=discord.Colour.green())
                    embed.add_field(name='Reason:', value=f'{reason}', inline=False)
                    embed.set_footer(text=f'Unbanned by {ctx.message.author.name}', icon_url=ctx.message.author.avatar_url_as(static_format='png'))
                    gbanned_users_c.delete_one(query)
                    await ctx.send(embed=embed)
                    print(f'{user} ({user.id}) has been unbanned from the federation by {ctx.message.author}\nReason{reason}')
                except Exception as e:
                    await ctx.send('An unknown error has occured, sent error log to HQ.')
                    print(f"[ERROR] CMD|UNGBAN: {e}")

            else:
                return await ctx.send(f"{user} ({user.id}) is not gbanned!")

# ---------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Gban(bot))
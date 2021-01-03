# Greetings cog by Doz
# ---------------------------------------------------------------------------
import discord, asyncio, random, pymongo, datetime, json
from pymongo import MongoClient
from discord import Member, Webhook, RequestsWebhookAdapter, File
from discord.ext.commands import Bot, has_permissions
from discord.ext import commands
from os import remove
# ---------------------------------------------------------------------------
# Webhook logging
errorlogs_webhook = Webhook.partial(746156734019665929, "i88z41TM5VLxuqnbIdM7EjW1SiaK8GkSUu0H3fOTLBZ9RDQmcOG0xoz6P5j1IafoU1t5",\
 adapter=RequestsWebhookAdapter()) #errorlogs in HQ
# ---------------------------------------------------------------------------
# Load configuration file
with open('config.json') as a:
    config = json.load(a) 
# ---------------------------------------------------------------------------
# MongoDB Configuration
mongosrv = config.get("mongosrv")
cluster = MongoClient(mongosrv)
db = cluster["mcreaper"]
# Collections
welcmsg = db["welcmsg"]
# ---------------------------------------------------------------------------
# Program Defs

# ---------------------------------------------------------------------------

class Greetings(commands.Cog):
    """Commands for greetings"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def greetingshelp(self, ctx):
        """Help page for ..."""

        embed =discord.Embed(title="GREETINGS HELP", description="These are the commands that can be used for custom join/leave messages.", colour=discord.Colour.red())
        embed.add_field(name="COMMANDS", value="- `greetings help` Shows help for greetings.", inline=False)
        await ctx.send(embed=embed)

    # Greetings
    @commands.group(invoke_without_command=True)
    @has_permissions(manage_guild=True)
    async def greetings(self, ctx, *, message=None):
        """Set greeting message in ctx.channel"""

        query = {'_id': ctx.guild.id}
        post = {'_id': ctx.guild.id, 'chanid': ctx.message.channel.id, 'msg': message, 'msgleave' : 'none'}

        if ctx.invoked_subcommand is None:

            if message == None:
                if (welcmsg.count_documents(query) == 1):
                    message = welcmsg.find_one(query)['msg']
                else:
                    return await ctx.send('See `greetings help` for details')

            if (welcmsg.count_documents(query) == 1):
                welcmsg.update_one(query, {"$set": {'chanid': ctx.message.channel.id, 'msg': message}})
                return await ctx.send(f'The greetings message will now be send here.\ngreetings message:\n{welcmsg.find_one(query)["msg"]}')
            
            welcmsg.insert_one(post)
            await ctx.send('This channel will now be used to send a greetings message whenever someone joins this server.\nIf you would like to change the greetings message then run this command again in the channel you want to set.\nIf you want to turn off greetings message then run `greetings off`\nSee `greetings help` for advanced usuage.')

    @greetings.command(aliases=['leave'])
    @has_permissions(manage_guild=True)
    async def greetings_leave(self, ctx, *, message=None):
        """Set leave message in channel from database"""

        query = {'_id': ctx.guild.id}

        if message == None:
            return await ctx.send('See `greetings help` for details')

        if (welcmsg.count_documents(query) == 1):
            welcmsg.update_one(query, {"$set": {'msgleave': message}})
            return await ctx.send(f'Updated message for on user leave.\n**If you want to disable Goodbye messages then type `greetings leave none`**\nGoodbye message:\n{welcmsg.find_one(query)["msgleave"]}')
        else:
            await ctx.send('You have not setup greetings yet!')

    @greetings.command(aliases=['help'])
    @has_permissions(manage_guild=True)
    async def greetings_help(self, ctx):
        """Shows greetings help"""

        await ctx.send('```Set the current channel as a greetings/goodbye channel where anytime a user joins/leaves the server, the bot will send the specified message on this channel.\n\ngreetings <message> - set message on join.\ngreetings leave <message> set message on leave.\nUsable terms:\n\n{mention} - mentions the user joined.\n{user} - displays username#discriminator.\n{username} - displays username.\n{userid} - displays userid.\n{servername} - displays server name.\n{serverid} - displays serverid.\n{serverowner} - displays server owner username#discriminator.\n{membercount} - displays the number of users in the server.\n{truemembercount} - displays the number of humans in the server.\n{userbirth} - displays the creation date of the user.\n{userage} - displays the age of the user account.\n{serverbirth} - displays the creation date of the server.```\n\n`greetings raw` - shows greetings message without format.\n`greetings off` - disables greetings message.')

    @greetings.command(aliases=['raw', 'noformat'])
    @has_permissions(manage_guild=True)
    async def greetings_raw(self, ctx):
        """Return the greetings message but without formatting"""

        query = {'_id': ctx.guild.id}

        if (welcmsg.count_documents(query) == 1):
            await ctx.send(f"greetings message:\n{welcmsg.find_one(query)['msg']}")
            return await ctx.send(f"Goodbye message:\n{welcmsg.find_one(query)['msgleave']}")

        await ctx.send('You have not setup greetings yet!')

    @greetings.command(aliases=['off'])
    @has_permissions(manage_guild=True)
    async def greetings_off(self, ctx):
        """Disable greetings"""

        query = {'_id': ctx.guild.id}

        if (welcmsg.count_documents(query) == 1):
            welcmsg.delete_one(query)
            return await ctx.send('Disabled greetings message.')

        await ctx.send('You have not setup greetings yet!')
# ---------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Greetings(bot))
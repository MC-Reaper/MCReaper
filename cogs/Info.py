# Info cog by Doz
# ---------------------------------------------------------------------------
import discord, asyncio, random, json, pymongo
from pymongo import MongoClient
from discord import Member, Webhook, RequestsWebhookAdapter
from discord.ext.commands import Bot
from discord.ext import commands
# ---------------------------------------------------------------------------
# Load configuration file
with open('config.json') as a:
    config = json.load(a)
# ---------------------------------------------------------------------------
BOT_OWNER_ID = int(config.get("bot_owner_id"))
BOT_INVITE_LINK = config.get("bot_invite")
HQ_SERVER_INVITE = config.get("server_invite")
# ---------------------------------------------------------------------------
# MongoDB Configuration
mongosrv = config.get("mongosrv") # Add your mongosrv link in config.json.
cluster = MongoClient(mongosrv, serverSelectionTimeoutMS = 2500)
db = cluster["mcreaper"]
# Collections
gbanned_users_c = db["gbanned_users"]
sudo_users_c = db["sudo_users"]
userbio_c = db["userbio"]
# ---------------------------------------------------------------------------
# Webhooks
errorlogs_webhook = Webhook.partial(746156734019665929, "i88z41TM5VLxuqnbIdM7EjW1SiaK8GkSUu0H3fOTLBZ9RDQmcOG0xoz6P5j1IafoU1t5",\
 adapter=RequestsWebhookAdapter()) #errorlogs in HQ
# ---------------------------------------------------------------------------
def RandomColour():
    """Generates random Colours"""

    randColour = discord.Colour(random.randint(0x000000, 0xFFFFFF))
    return randColour
# ---------------------------------------------------------------------------
class Info(commands.Cog):
    """Commands for information"""
    
    def __init__(self, bot):
        self.bot = bot

    # Info
    # Userinfo
    @commands.group(invoke_without_command=True, aliases=['user', 'uinfo', 'info', 'ui'])
    async def userinfo(self, ctx, *, txt=""):
        """Obtain info of a user"""
        
        gban_flag = "Not Banned"
        gban_reason = ""

        if ctx.invoked_subcommand is None:

            if txt:
                if txt == "me":
                    user = ctx.message.author
                else:
                    try:
                        user = ctx.message.mentions[0]
                    except IndexError:
                        user = ctx.guild.get_member_named(txt)
                    if not user:
                        try:
                            user = await commands.MemberConverter().convert(ctx, txt)
                        except:
                            pass
                    if not user:
                        try:
                            user = await self.bot.fetch_user(int(txt))
                        except ValueError:
                            user = None
                    if user == None:
                        await ctx.send("I may be blind because I couldn't find that user anywhere!")
                        return
                    if not user:
                        await ctx.send("I may be blind because I couldn't find that user anywhere!")
                        return
            else:
                user = ctx.message.author

            avi = user.avatar_url_as(static_format='png')

            if isinstance(user, discord.Member):
                role = user.top_role.name
                if role == "@everyone":
                    role = "No roles"
                voice_state = "Not in any VC" if not user.voice else user.voice.channel
            em = discord.Embed(timestamp=ctx.message.created_at, colour=RandomColour())
            em.add_field(name='User ID', value=user.id, inline=False)

            if isinstance(user, discord.Member):
                em.add_field(name='Nick', value=user.nick, inline=False)
                em.add_field(name='In Voice', value=voice_state, inline=False)
                em.add_field(name='Highest Role', value=role, inline=False)
            em.add_field(name='Account Created', value=user.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S (UTC)'), inline=False)

            if isinstance(user, discord.Member):
                em.add_field(name='Join Date', value=user.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S (UTC)'), inline=False)
            
            query = {"_id": user.id}
            if (gbanned_users_c.count_documents(query) == 1):
                gban_flag = "Banned"
                gban_reason = f'\nReason: {gbanned_users_c.find_one(query)["reason"]}'
            em.add_field(name='Federation Ban Status', value=f"{gban_flag} {gban_reason}", inline=False)

            if (userbio_c.count_documents(query) == 1):
                em.add_field(name='About User', value=userbio_c.find_one(query)['bio'], inline=False)

            if (sudo_users_c.count_documents(query) == 1):
                em.add_field(name='This is one of my sudo users!', value=f"Hi master {user.name}", inline=False)

            mutual_servers_list = []
            for guilds in self.bot.guilds:
                try:
                    mutual_server = await guilds.fetch_member(user.id)
                    if mutual_server:
                        mutual_servers_list.append(str(guilds))
                    if not mutual_server:
                        pass
                except:
                    pass
            em.add_field(name='Mutual Servers', value=f'I have seen this user in {len(mutual_servers_list)} servers.')

            em.set_thumbnail(url=avi)
            em.set_author(name=user, icon_url=user.avatar_url_as(static_format='png'))
            await ctx.send(embed=em)

    # Userinfo avi
    @userinfo.command(aliases=['pfp'])
    async def avi(self, ctx, txt=""):
        """View bigger version of user's avatar. Ex: [p]info avi @user"""

        if txt:
            if txt == "me":
                user = ctx.message.author
            else:
                try:
                    user = ctx.message.mentions[0]
                except IndexError:
                    user = ctx.guild.get_member_named(txt)
                if not user:
                    try:
                        user = await commands.MemberConverter().convert(ctx, txt)
                    except:
                        pass
                if not user:
                    try:
                        user = await self.bot.fetch_user(int(txt))
                    except ValueError:
                        user = None
                if user == None:
                    await ctx.send("I may be blind because I couldn't find that user anywhere!")
                    return
                if not user:
                    await ctx.send("I may be blind because I couldn't find that user anywhere!")
                    return
        else:
            user = ctx.message.author

        avi = user.avatar_url_as(static_format='png')
        em = discord.Embed(colour=RandomColour())
        em.set_image(url=avi)
        await ctx.send(embed=em)
        await ctx.message.delete()

    @userinfo.error
    async def userinfo_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('`ui <user> or ui avi <user>`')
        else:
            await ctx.send('An unknown error has occured, sent error log to HQ.')
            errorlogs_webhook.send(f"```[ERROR] CMD|UI/AVI: {str(error)}```")

    @commands.command(aliases=['server', 'sinfo', 'si'])
    async def serverinfo(self, ctx, *, lol = None):

        if lol == None:
            try:
                server = ctx.message.guild
                role_count = len(server.roles)
                emoji_count = len(server.emojis)
                channel_count = len([x for x in server.channels if type(x) == discord.channel.TextChannel])
                online = 0
                for i in server.members:
                    if str(i.status) == 'online' or str(i.status) == 'idle' or str(i.status) == 'dnd':
                        online += 1
                all_users = []
                for user in server.members:
                    all_users.append('{}#{}'.format(user.name, user.discriminator))
                all_users.sort()
                # all = '\n'.join(all_users)
                em = discord.Embed(colour=RandomColour())
                em.add_field(name='Name', value=server.name, inline=False)
                em.add_field(name='Owner', value=server.owner, inline=False)
                em.add_field(name='Members', value=server.member_count, inline=False)
                em.add_field(name='Currently Online', value=online, inline=False)
                em.add_field(name='Text Channels', value=str(channel_count), inline=False)
                em.add_field(name='Region', value=server.region, inline=False)
                em.add_field(name='Verification Level', value=str(server.verification_level), inline=False)
                em.add_field(name='Number of roles', value=str(role_count), inline=False)
                em.add_field(name='Number of emotes', value=str(emoji_count), inline=False)
                em.add_field(name='Created At', value=server.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S (UTC)'), inline=False)
                em.set_thumbnail(url=server.icon_url)
                em.set_author(name='Server Info', icon_url=f"{user.avatar_url_as(static_format='png')}")
                em.set_footer(text='Server ID: %s' % server.id)
                await ctx.send(embed=em)
            except Exception as e:
                await ctx.send(e)
        elif lol == 'avi':
            server = ctx.message.guild
            try:
                em = discord.Embed(colour=RandomColour())
                em.set_image(url=server.icon_url)
                await ctx.send(embed=em)
            except Exception as e:
                await ctx.send(e)
        else:
            return await ctx.send('`si or si avi`')

    # Owner
    @commands.command()
    async def owner(self, ctx):
        server = ctx.message.guild
        avi = server.owner.avatar_url_as(static_format='png')
        if ctx.message.author.id == BOT_OWNER_ID:
            bowner = f'You are the bot owner! Hi **{ctx.author.name}**!'
        else:
            bowner = 'You are not the bot owner! Buzz off!'
            
        embed = discord.Embed(title='Who is the Owner?', description=f"**{server.owner}** is the owner of this server.\nMore details of the owner:\nAccount birthday: {server.owner.created_at.__format__('%A, %d. %B %Y')}\nAccount joined server: {server.owner.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S')}", colour=RandomColour())
        
        embed.add_field(name='Are you the bot owner?', value=bowner, inline=False)
        embed.set_author(name='Owner', icon_url=avi)
        
        await ctx.send(embed=embed)

    # Invite
    @commands.command()
    async def invite(self, ctx):
        """Invite command"""

        avi=self.bot.user.avatar_url_as(static_format='png')

        em = discord.Embed(
        description = 'Invite our bot to your server or join our discord!',
        colour = RandomColour()
        )
        em.add_field(name='Bot invite', value=f'[Invite me to your server!]({BOT_INVITE_LINK})', inline=True)
        em.add_field(name='Server invite', value=f'[MC-R HQ]({HQ_SERVER_INVITE})', inline=True)
        em.set_author(name='Invitation', icon_url=avi)
        em.set_footer(text='Created by Doz')
        
        await ctx.send(embed=em)

    # Report cmd
    @commands.command()
    async def report(self, ctx, *, msg = None):
        """Report command"""

        async with ctx.typing():

            if msg == None:
                return await ctx.send('`report <msg>`')
            
            try:
                server_invites = await ctx.guild.invites()
                for server_invite in server_invites:
                    server_invite = server_invite
            except:
                server_invite = "Couldn't obtain server invite."

            userID = ctx.message.author.id
            user = ctx.message.author
            hqchannel = self.bot.get_channel(746162901017952318)
            embed = discord.Embed(
            timestamp = ctx.message.created_at,
            description = msg,
            colour = discord.Colour.red()
            )
            embed.set_author(name=f'New report by: {user}', icon_url=user.avatar_url_as(static_format='png'))
            embed.add_field(name="Reporter's ID:", value=userID)
            embed.add_field(name="Reported from:", value=server_invite.url)
            embed.add_field(name="Channel:", value=ctx.channel.id, inline=False)
            embed.add_field(name="Guild_ID:", value= ctx.guild.id, inline=False)
                
            await hqchannel.send(embed=embed)
            await ctx.message.delete()
            await ctx.send("Report was sent to TGB. \nPlease don't abuse abuse this command!")

    # Suggest cmd
    @commands.command()
    async def suggest(self, ctx, *, msg = None):
        """Suggest command"""

        async with ctx.typing():

            if msg == None:
                return await ctx.send('`suggest <msg>`')

            try:
                server_invites = await ctx.guild.invites()
                for server_invite in server_invites:
                    server_invite = server_invite
            except:
                server_invite = "Couldn't obtain server invite."

            userID = ctx.message.author.id
            user = ctx.message.author
            hqchannel = self.bot.get_channel(746163888910762084)
            embed = discord.Embed(
            timestamp = ctx.message.created_at,
            description = msg,
            colour = discord.Colour.red()
            )
            embed.set_author(name=f'New suggestion by: {user}', icon_url=user.avatar_url_as(static_format='png'))
            embed.add_field(name="Suggester's ID:", value=userID)
            embed.add_field(name="Suggested from:", value=server_invite.url)
            embed.add_field(name="Channel:", value=ctx.channel.id, inline=False)
            embed.add_field(name="Guild_ID:", value= ctx.guild.id, inline=False)
                
            await hqchannel.send(embed=embed)
            await ctx.message.delete()
            await ctx.send("Suggestion was sent to TGB. \nPlease don't abuse abuse this command!")

# ---------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Info(bot))
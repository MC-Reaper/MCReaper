# ---------------------------------------------------------------------------
# Modules
try:
    import discord, json, asyncio, random, nekos, pyfiglet, pymongo, reapertools
    from datetime import datetime
    from pymongo import MongoClient
    from discord import Member, Game, Webhook, RequestsWebhookAdapter, File
    from discord.ext import commands
    from discord.ext.commands import Bot, has_permissions
    from platform import python_version, platform
    from os import remove, listdir
except ImportError:
    print(
    'You baka! You forgot to install the required modules in requirements.txt!',
    '\nInstall them with pip install -r requirements.txt'
    )
    exit()
# ---------------------------------------------------------------------------
# Load configuration file
with open('config.json') as a:
    config = json.load(a)
# ---------------------------------------------------------------------------
# Configuration
# Please see config.json
# ! DO NOT EDIT !
default_prefix = config.get("prefix")
token = config.get("bot_token") # bot_token in config.json.
mongosrv = config.get("mongosrv") # Add your mongosrv link in config.json.
BOT_OWNER_ID = int(config.get("bot_owner_id")) # Add your userid in config.json.
# --------------------------------------------------------------------------
BOT_VERSION = f'Python: v{python_version()} | Discord.py: v{discord.__version__} | Bot: v0.16'
DOZ_DISCORD = 'Doz#1040'
# ---------------------------------------------------------------------------
HQ_SERVER_INVITE = config.get("server_invite")
BAN_GIF = config.get("ban_gif")
NUKE_GIF = config.get("nuke_gif")
NUKE_LAUNCH_GIF = config.get("nuke_launch_gif")
CHANGELOG_MESSAGE = "Fixed everyone ping loophole\nMinor changes."
CHANGELOG_DATE = '03/02/2021'
# ! DO NOT EDIT !
# ---------------------------------------------------------------------------
# MongoDB Configuration
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
welcmsg = db["welcmsg"]
afk_c = db["afk"]
# ---------------------------------------------------------------------------
# Prefix Mgt
def get_prefix(bot, msg):
    """Get prefix from mongo database"""

    query = {"_id": msg.guild.id}

    if (guild_prefixes_c.count_documents(query) == 1):

        guild_prefixes : str = guild_prefixes_c.find_one(query)["prefix"]
        return commands.when_mentioned_or(*guild_prefixes)(bot, msg)

    return commands.when_mentioned_or(default_prefix)(bot, msg)
# ---------------------------------------------------------------------------
# Boot
print(
f"""
███╗   ███╗ ██████╗    ██████╗ ███████╗ █████╗ ██████╗ ███████╗██████╗ 
████╗ ████║██╔════╝    ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝██╔══██╗
██╔████╔██║██║         ██████╔╝█████╗  ███████║██████╔╝█████╗  ██████╔╝
██║╚██╔╝██║██║         ██╔══██╗██╔══╝  ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
██║ ╚═╝ ██║╚██████╗    ██║  ██║███████╗██║  ██║██║     ███████╗██║  ██║
╚═╝     ╚═╝ ╚═════╝    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝

By {DOZ_DISCORD} | Ver: {BOT_VERSION}
""")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command("help")
botstartTime = datetime.utcnow()
# ---------------------------------------------------------------------------
# Webhooks
# TODO: Make webhook logging optional
logs_webhook = Webhook.partial(746158498181808229, "JJNzXDenBhg5t97X7eAX52bjhzL0Oz-dS5b_XKoAzkqjQvA90tWva-5fWibrcEQb2WD5",\
 adapter=RequestsWebhookAdapter())

reaper_logs_webhook = Webhook.partial(746157945468747776, "lOrgfZFXSTt32nQq9qzZgeNewBxfaM--bTUT4EFg9jgAWhGGfBMcVUSijddymaEQvgWl",\
 adapter=RequestsWebhookAdapter())

gbans_webhook = Webhook.partial(746155689033990144, "V4QGR7UAO3HRGTYb2j8iUNFN4F1utX2CV5RQ3bWQSH_LGartc0lgAXPKEFiMUHxGL6kb",\
 adapter=RequestsWebhookAdapter())

joinleave_webhook = Webhook.partial(746157465606946847, "SOz8ky2uDPiNfdjntY4H40jdpm9YHVM1kVRIv_LcgN_hKu7e269oAHkDGUgtxPdj8y6Q",\
 adapter=RequestsWebhookAdapter())

errorlogs_webhook = Webhook.partial(746156734019665929, "i88z41TM5VLxuqnbIdM7EjW1SiaK8GkSUu0H3fOTLBZ9RDQmcOG0xoz6P5j1IafoU1t5",\
 adapter=RequestsWebhookAdapter())
# ---------------------------------------------------------------------------
# Cog loader
if __name__ == '__main__':
    for cog in listdir("./cogs"):
        if cog.endswith(".py"):
            try:
                cog = f"cogs.{cog.replace('.py', '')}"
                bot.load_extension(cog)
            except Exception as e:
                cogerrlg = f"[CRITICAL] BOT|COGS: {cog} could not be loaded!\n{e}"
                print(cogerrlg)
                errorlogs_webhook.send(f"```{cogerrlg}```")
            else:
                print(f"[INFO] BOT|COGS: {cog} has been loaded!")
# ---------------------------------------------------------------------------
# Program Defs
def RandomColour():
    """Generates random colours for embed"""

    randcolour = discord.Colour(random.randint(0x000000, 0xFFFFFF))
    return randcolour

async def send_to_log_channel(gld=discord.Guild, *, text=None, emt=None, fle: File = None):
    """Send info to log channel which can be fetched using MongoDB"""

    query = {"_id" : gld.id}

    if (chatlog.count_documents(query) == 1):

        chatlog_id = chatlog.find_one(query)['chanid']
        logs_channel = bot.get_channel(chatlog_id)

        if not logs_channel:
            lgerr = f'[NOTICE] BOT|LOGS: Could not find channel for logging in {gld.name} ({gld.id}) so the DB has been deleted.'
            chatlog.delete_many(query)
            print(lgerr)
            logs_webhook.send(f'```{lgerr}```')
        
        else:
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
# Events
@bot.event
async def on_ready():
    """When the bot has started up"""

    # TODO: Add change presence commands and use MongoDB for it to survive restarts. 

    await bot.change_presence(activity=discord.Streaming(name=f"-help | Overseeing {len(bot.guilds)} guilds", url='https://www.twitch.tv/artia_hololive'))

    em = discord.Embed(title='MC Reaper Status', description=f'MC Reaper is running!', colour=RandomColour())
    em.add_field(name='Bot version:', value=BOT_VERSION, inline=False)
    logs_webhook.send(embed=em)
    print(f'[INFO] BOT|BOOT: MC Reaper is running!\n[INFO] BOT|BOOT: Logged in as {bot.user} | {bot.user.id}')

@bot.event
async def on_guild_join(guild):
    """When the bot joins a guild"""

    ogr = f'[INFO] BOT|JOIN: Joined guild, {guild.name} ({guild.id}) owned by {guild.owner} ({guild.owner.id})'
    print(ogr)
    joinleave_webhook.send(f'```{ogr}```')

@bot.event
async def on_guild_remove(guild):
    """When the bot leaves a guild"""

    ogr1 = f'[INFO] BOT|LEAVE: Left guild, {guild.name} ({guild.id})'
    print(ogr1)
    joinleave_webhook.send(f'```{ogr1}```')

    wquery = {"guild_id" : guild.id}
    gquery = {"GuildID": str(guild.id)}
    query = {"_id" : guild.id}

    try:
        if (warn_c.count_documents(wquery) >= 1):
            resultw = warn_c.delete_many(wquery)
            mjrp1 = f'[INFO] WARN|DB: Deleted {resultw.deleted_count} queries of {guild.name} ({guild.id}) as the bot was removed.'
            print(mjrp1)
            logs_webhook.send(f"```{mjrp1}```")
        if (nsfw_flag.count_documents(query) >= 1):
            resultn = nsfw_flag.delete_many(query)
            mjrp2 = f'[INFO] NSFW|DB: Deleted {resultn.deleted_count} queries of {guild.name} ({guild.id}) as the bot was removed.'
            print(mjrp2)
            logs_webhook.send(f"```{mjrp2}```")
        if (chatlog.count_documents(query) >= 1):
            resultc = chatlog.delete_many(query)
            mjrp3 = f'[INFO] CHATLOG|DB: Deleted {resultc.deleted_count} queries of {guild.name} ({guild.id}) as the bot was removed.'
            print(mjrp3)
            logs_webhook.send(f"```{mjrp3}```")
        if (welcmsg.count_documents(query) >= 1):
            resultwc = welcmsg.delete_many(query)
            mjrp4 = f'[INFO] WELCOME_MSG|DB: Deleted {resultwc.deleted_count} queries of {guild.name} ({guild.id}) as the bot was removed.'
            print(mjrp4)
            logs_webhook.send(f"```{mjrp4}```")
        if (afk_c.count_documents(gquery) >= 1):
            resultafk = welcmsg.delete_many(gquery)
            mjrp5 = f'[INFO] AFK|DB: Deleted {resultafk.deleted_count} queries of {guild.name} ({guild.id}) as the bot was removed.'
            print(mjrp5)
            logs_webhook.send(f"```{mjrp5}```")
    except Exception as e:
        mjrp6 = f'[ERROR] ONMEMBERJOIN|DATABASE: {e}'
        print(mjrp6)
        errorlogs_webhook.send(f'```{mjrp6}```')

@bot.event
async def on_member_join(member):
    """When a member joins"""

    query = {"_id": member.id}
    guild = member.guild

    if (welcmsg.count_documents({"_id": guild.id}) == 1):

        replace_dict = {'{mention}': member.mention, '{user}': str(member), '{username}': str(member.name), '{userid}': str(member.id), '{servername}': str(guild.name), '{serverid}': str(guild.id), '{serverowner}': str(guild.owner), '{membercount}': str(len(guild.members)), '{truemembercount}': str(len([m for m in guild.members if not m.bot])), '{userbirth}': member.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S (UTC)'), '{userage}': reapertools.datediff_humanize(member.created_at, datetime.utcnow()), '{serverbirth}': guild.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S (UTC)')}
        raw_welcome_msg = welcmsg.find_one({"_id": guild.id})['msg']
        translated_text = reapertools.rtwdv(raw_welcome_msg, replace_dict)

        welchan_id = welcmsg.find_one({"_id": guild.id})['chanid']
        welcome_channel = bot.get_channel(welchan_id)

        if member.id == BOT_OWNER_ID:
            translated_text = translated_text + '\nMy creator has joined the server.'

        if not welcome_channel:
            lgerr = f'[WARNING] BOT|LOGS: Could not find channel for welcome message in {guild.name} ({guild.id})!'
            print(lgerr)
            errorlogs_webhook.send(f'```{lgerr}```')
        else:
            await welcome_channel.send(content=translated_text)

    if (chatlog.count_documents({"_id": guild.id}) == 1):

        gban_flag = "Not Banned"
        gban_reason = ""

        avi = member.avatar_url_as(static_format='png')
        em = discord.Embed(colour=RandomColour())
        em.add_field(name='User ID', value=member.id, inline=False)
        em.add_field(name='Account Created', value=member.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S (UTC)'), inline=False)
        if isinstance(member, discord.Member):
            em.add_field(name='Join Date', value=member.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S (UTC)'), inline=False)
        if (gbanned_users_c.count_documents(query) == 1):
            gban_flag = "Banned"
            gban_reason = f'\nReason: {gbanned_users_c.find_one(query)["reason"]}'
        em.add_field(name='Federation Ban Status', value=f"{gban_flag} {gban_reason}", inline=False)
        if (userbio_c.count_documents(query) == 1):
            em.add_field(name='About User', value=userbio_c.find_one(query)['bio'], inline=False)
        if (sudo_users_c.count_documents(query) == 1):
            em.add_field(name='This is one of my sudo users!', value=None, inline=False)
        em.set_thumbnail(url=avi)
        em.set_author(name=f'{member} joined.', icon_url=avi)

        await send_to_log_channel(gld=guild, emt=em)

    if (gbanned_users_c.count_documents(query) == 1):
        try:
            gban_user_reason : str = gbanned_users_c.find_one(query)["reason"]
            logs_webhook.send(f'```[INFO] AUTOMOD: {member} ({member.id}) was banned from entering {guild.name}!\nREASON GBANNED: {gban_user_reason}```')
            await member.ban(reason=gban_user_reason)
            await send_to_log_channel(gld=guild, text=f'{member} ({member.id}) was denied access to your server due to being in the global ban database.\nReason for GBAN: {gban_user_reason}')
        except Exception as e:
            errorlogs_webhook.send(f'```[WARNING] AUTOMOD: GBAN OF {member} ({member.id}) in {guild.name} FAILED! {e}```')

@bot.event
async def on_member_remove(member):
    """When a member leaves"""

    guild = member.guild
    query = {"GuildID": guild.id, "UserID": member.id}
    gquery = {"_id": guild.id}

    if (welcmsg.count_documents(gquery) == 1):

        replace_dict = {'{mention}': member.mention, '{user}': str(member), '{username}': str(member.name), '{userid}': str(member.id), '{servername}': str(guild.name), '{serverid}': str(guild.id), '{serverowner}': str(guild.owner), '{membercount}': str(len(guild.members)), '{truemembercount}': str(len([m for m in guild.members if not m.bot])), '{userbirth}': member.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S (UTC)'), '{userage}': reapertools.datediff_humanize(member.created_at, datetime.utcnow()), '{serverbirth}': guild.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S (UTC)')}
        raw_welcome_msg = welcmsg.find_one(gquery)['msgleave']

        if raw_welcome_msg == 'none':
            pass
        else:
            translated_text = reapertools.rtwdv(raw_welcome_msg, replace_dict)

            welchan_id = welcmsg.find_one(gquery)['chanid']
            welcome_channel = bot.get_channel(welchan_id)

            if not welcome_channel:
                lgerr = f'[WARNING] BOT|LOGS: Could not find channel for welcome message in {guild.name} ({guild.id})!'
                print(lgerr)
                errorlogs_webhook.send(f'```{lgerr}```')
            else:
                await welcome_channel.send(content=translated_text)

    if (chatlog.count_documents(gquery) == 1):

        avi = member.avatar_url_as(static_format='png')
        em = discord.Embed(colour=discord.Colour.red(), timestamp=datetime.utcnow())
        em.set_author(name=f'{member} ({member.id}) left.', icon_url=avi)

        await send_to_log_channel(gld=guild, emt=em)

    try:
        if (warn_c.count_documents(query) >= 1):
            resultw = warn_c.delete_many(query)
            logs_webhook.send(f'WARN DB: Deleted {resultw.deleted_count} queries of {guild.name} ({guild.id}) as the bot was removed.')
        if (afk_c.count_documents(query) >= 1):
            resultafk = welcmsg.delete_many(query)
            logs_webhook.send(f'AFK DB: Deleted {resultafk.deleted_count} queries of {guild.name} ({guild.id}) as the bot was removed.')
    except Exception as e:
        errlog = f'[ERROR] DATABASE|ONMEMBERREMOVE: {e}'
        print(errlog)
        errorlogs_webhook.send(f'```{errlog}```')

@bot.event
async def on_member_update(userb, usera):
    """When a member updates"""

    checkb = userb.nick
    checka = usera.nick

    if checkb == checka:
        pass

    elif (chatlog.count_documents({"_id": userb.guild.id}) == 1):
        
        avib=userb.avatar_url_as(static_format='png')
        avia=usera.avatar_url_as(static_format='png')
        em = discord.Embed(description=f'User {userb} ({userb.id}) has been updated.', colour=discord.Colour.orange(), timestamp=datetime.utcnow())
        if userb.nick != usera.nick:
            em.add_field(name='Nickname changed', value=f'**Old nickname:** {userb.nick}\n**New nickname:** {usera.nick}')
        em.set_author(name='User updated', icon_url=avia)
        em.set_thumbnail(url=avib)

        await send_to_log_channel(gld=userb.guild, emt=em)

@bot.event
async def on_user_update(userb, usera):
    """When a user updates"""

    checkb = userb.name, userb.discriminator, userb.avatar
    checka = usera.name, usera.discriminator, usera.avatar

    if userb.bot == True:
        return

    if checkb == checka:
        pass

    else:
        for guilds in list(bot.guilds):

            try:
                membera = await guilds.fetch_member(usera.id)

                date = datetime.utcnow()

                if (chatlog.count_documents({"_id": membera.guild.id}) == 1):
                    avib=userb.avatar_url_as(static_format='png')
                    avia=usera.avatar_url_as(static_format='png')
                    em = discord.Embed(description=f'User {userb} has been updated.', colour=discord.Colour.orange())
                    if userb.name != usera.name:
                        em.add_field(name='Username changed', value=f'**Old username:** {userb.name}\n**New username:** {usera.name}')
                    if userb.discriminator != usera.discriminator:
                        em.add_field(name='Discriminator changed', value=f'**Old discriminator:** {userb.discriminator}\n**New discriminator:** {usera.discriminator}')
                    if userb.avatar != usera.avatar:
                        em.add_field(name='Avatar changed', value='**Old avatar:** ➡️\n**New Avatar:** ⬇️', inline=False)
                        em.set_image(url=avia)
                    em.set_author(name='User updated', icon_url=avia)
                    em.set_thumbnail(url=avib)
                    em.set_footer(text=f'User ID: {usera.id} | {date.__format__("%d/%m/%y @ %H:%M")} UTC')

                    await send_to_log_channel(gld=membera.guild, emt=em)

            except:
                pass

@bot.event
async def on_invite_create(invite):
    """When an invite has been created"""

    guild = invite.guild
    query = {"_id": guild.id}

    if (chatlog.count_documents(query) == 1):

        age = str(invite.max_age)
        if age == '0':
            age = 'Indefinite'

        uses_until_expire = str(invite.max_uses)
        if uses_until_expire == '0':
            uses_until_expire = 'Infinite'

        inviter = invite.inviter
        if not inviter:
            inviter = "Couldn't figure out who created this invite."

        inviter_pfp = inviter.avatar_url_as(static_format='png')
        if not inviter_pfp:
            inviter_pfp = 'https://1000logos.net/wp-content/uploads/2017/12/Pornhub-symbol.jpg'

        invite_channel = invite.channel
        if not invite_channel:
            invite_channel = "Couldn't figure out what channel this invite is for."

        url = invite.url

        em = discord.Embed(colour = discord.Colour.blue(), timestamp=datetime.utcnow())
        em.set_author(name='Invite Created', icon_url=inviter_pfp)
        em.add_field(name='Invite url', value=url)
        em.add_field(name='Expiry date (seconds)', value=age)
        em.add_field(name='Uses until invalid', value=uses_until_expire)
        em.add_field(name='Invite channel', value=f'<#{invite_channel.id}>')
        em.add_field(name='Invite Creator', value=f'{inviter} ({inviter.id})')

        await send_to_log_channel(gld=guild, emt=em)

@bot.event
async def on_message(message):
    """When a message has been sent"""

    user = message.author
    if user.id == bot.user.id:
        return

    guild = message.channel.guild
    if not guild:
        return

    query = {"UserID": str(user.id), 'GuildID': str(guild.id)}

    if (afk_c.count_documents(query) == 1):
        afk_c.delete_one(query)
        await message.channel.send(f'Wuddup {user.mention}! I removed your AFK!')

    if message.mentions:
        for mention in message.mentions:
            afk_c_list = list(afk_c.find({'GuildID': str(guild.id)}))
            for x in afk_c_list:
                if str(mention.id) in x['UserID'] and str(user.id) not in x['UserID']:

                    afksince = reapertools.datediff_humanize(x['Timestamp'], datetime.utcnow())

                    reason = afk_c.find_one({"UserID": str(mention.id), "GuildID": str(guild.id)})['Reason']
                    await message.channel.send(f'{mention} is currently AFK: {reason}\nAFK {afksince} ago.')

    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    """When a message has been deleted"""

    try:
        guild = message.author.guild
    except:
        return

    if (sudo_users_c.count_documents({"_id": message.author.id}) == 1):
        pass
    
    else:
        query = {"_id": guild.id}

        if (chatlog.count_documents(query) == 1):

            user = message.author
            avi = user.avatar_url_as(static_format='png')
            msgcont = message.content
            msgid = message.id
            fle : File = None
            if not msgid:
                msgid = "Couldn't display the Message ID."
            if not msgcont:
                msgcont = "The message couldn't be obtained because it was either an embed or it was empty."
            if len(msgcont) > 1024:
                output = open("log.txt", "w+")
                output.write(f"From {message.author}:\n\n{msgcont}\n\nMessage created at: {message.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S')}\nMessage deleted at: {datetime.utcnow().__format__('%A, %d. %B %Y @ %H:%M:%S')}")
                output.close()
                fle = File("./log.txt")
                msgcont = "The message couldn't be displayed because it exceeded 1024 characters, uploaded as file instead."
            if message.embeds:
                msgcont = "The message couldn't be obtained because it was either an embed or it was empty."

            em = discord.Embed(colour=discord.Colour.red(), timestamp=datetime.utcnow())
            em.set_author(name='Message Deleted', icon_url=avi)
            em.add_field(name='User', value=f'{user} ({user.id})')
            em.add_field(name='Channel', value=f'<#{message.channel.id}>')
            em.add_field(name='Message ID', value=msgid)
            em.add_field(name='Content', value=msgcont)

            await send_to_log_channel(gld=guild, emt=em, fle=fle)

@bot.event
async def on_bulk_message_delete(messages):
    """When a set of messages has been deleted"""

    for message in messages:
        channel = message.channel
        guild = channel.guild
        if not guild:
            return

    query = {"_id": guild.id}

    if (chatlog.count_documents(query) == 1):

        deleted_messages_count = str(len(messages))

        em = discord.Embed(colour=discord.Colour.gold(), timestamp=datetime.utcnow())
        em.set_author(name='Bulk Messages Deleted')
        em.add_field(name='Count', value=deleted_messages_count)
        em.add_field(name='Channel', value=f'<#{channel.id}>')

        await send_to_log_channel(gld=guild, emt=em)
# ---------------------------------------------------------------------------
# Global Error handlers
@bot.event
async def on_command_error(ctx, error):
    """Handles errors."""

    msgcont = str(ctx.message.content)
    errorstring = str(error)
    error = getattr(error, 'original', error)
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.errors.CheckFailure):
        errorstr = f'You are not authorized to use this command!'
    elif isinstance(error, commands.BotMissingPermissions):
        errorstr = f'I cannot run this command, I am missing permissions!'
    elif isinstance(error, discord.errors.Forbidden):
        errorstr = f'Discord forbids this action!\n```{error}```'
    elif "Cannot send an empty message" in errorstring:
        errorstr = "Can't send an empty message!"
    elif "Unknown Message" in errorstring:
        errorstr = None
        pass
    else:
        errorstr = f"An error has occured! HQ will receive this error message!\n```{error}```"
        pwebstr = f"[ERROR] BOT|CMD: MSGCONT: {msgcont}\nError: {error}"
        try:
            errorlogs_webhook.send(pwebstr)
        except:
            errorlogs_webhook.send('An error has occured but it exceeded 2000 Chars, sending to console logs..')
            print(pwebstr)

    if errorstr == None:
        return

    err_embed = discord.Embed(description=errorstr, colour=discord.Colour.red())
    err_embed.set_author(name='Error', icon_url='https://www.freeiconspng.com/uploads/a-red-error-exclamation-sign-meaningful-official-round-26.png')
    return await ctx.send(embed=err_embed)

# ---------------------------------------------------------------------------
# Commands
# Regular users
@bot.group(invoke_without_command=True)
async def help(ctx):
    """Shows help"""

    if ctx.invoked_subcommand is None:

        async with ctx.typing():

            embed = discord.Embed(colour=RandomColour())
            embed.set_author(name=f'{bot.user.name} Help', icon_url=bot.user.avatar_url_as(static_format='png'))
            embed.set_footer(text='MC Reaper')
            embed.add_field(name='Commands', value='Command types:\n`<arg>` required.\n`[arg]` optional.\n\n- `changelog` What is new?\n- `afk <reason>` afk\n- `fetchtorrent` Torrent searcher (WIP).\n- `animesearch` Anime seacher (WIP).' , inline=False)
            embed.add_field(name='Pages', value="Use `help <page>` to navigate to different help sections.\n\n- `help fun` Help for fun commands.\n- `help info` Help for info commands.\n- `help google` Help for google commands.\n- `help greetings` Help for greetings commands (mod only)\n- `help mod` Help for moderator commands.", inline=False)
            embed.add_field(name='NSFW', value='Powered by nekos.life\n- `hentaibomb`\n- `nsfw <text>` Just enter nsfw for list of nsfw.', inline=False)
            embed.add_field(name='Bot information', value=f'{BOT_VERSION}\nCreated by: **{DOZ_DISCORD}**', inline=False)
            embed.set_thumbnail(url=ctx.message.author.avatar_url_as(static_format='png'))
            await ctx.send(embed=embed)

@help.command(aliases=['fun'])
async def fun_help(ctx):
    """Help page for Fun"""

    embed = discord.Embed(title="Fun Help", description="Commands for Fun", colour=RandomColour())
    embed.add_field(name='Commands', value='- `say <words>` You know what this does.\n- `shout <msg>` Shouts messages.\n- `ascii <text>` Prints text in ascii format.\n- `8ball <question>` Answers your questions!\n- `penis [user]` Checks your pp length.\n- `gayr8 <name>` Checks how gay anything is.\n- `waifur8 <name>` :heart:\n- `thotr8` BEGONE THOT!', inline=False)
    await ctx.send(embed=embed)


@help.command(aliases=['google'])
async def google_help(ctx):
    """Help page for Google"""

    embed = discord.Embed(title="Google Help", description="Commands for google search", colour=RandomColour())
    embed.add_field(name="Commands", value="`gsearch <query>` searches for the first 5 results.", inline=False)
    await ctx.send(embed=embed)

@help.command(aliases=['greetings'])
@has_permissions(manage_guild=True)
async def greetings_help(ctx):
    """Shows greetings help"""

    embed = discord.Embed(title="Greetings Help", description="Set the current channel as a greetings/goodbye channel where anytime a user joins/leaves the server, the bot will send the specified message on this channel.", colour=RandomColour())
    embed.add_field(name="Commands", value='```greetings <message> - set message on join.\ngreetings leave <message> set message on leave.\nUsable terms:\n\n{mention} - mentions the user joined.\n{user} - displays username#discriminator.\n{username} - displays username.\n{userid} - displays userid.\n{servername} - displays server name.\n{serverid} - displays serverid.\n{serverowner} - displays server owner username#discriminator.\n{membercount} - displays the number of users in the server.\n{truemembercount} - displays the number of humans in the server.\n{userbirth} - displays the creation date of the user.\n{userage} - displays the age of the user account.\n{serverbirth} - displays the creation date of the server.```\n\n`greetings raw` - shows greetings message without format.\n`greetings off` - disables greetings message.', inline=False)
    await ctx.send(embed=embed)

@help.command(aliases=['info'])
async def info_help(ctx):
    """Help for information"""

    embed = discord.Embed(title="Informaton Help", description="These are the commands that can be used to get information.", colour=RandomColour())
    embed.add_field(name="Commands", value="- `ping` Checks the bot's latency.\n- `report <message>` report bot issues to HQ.\n- `suggest <message>` Suggest changes to the bot to HQ\n- `invite` Get bot invite link and TGB server invite.\n- `userinfo <@user>` Gets info about someone\n- `serverinfo` gets server info\n- `owner` Whos the owner of the server?", inline=False)
    await ctx.send(embed=embed)

@help.command(aliases=['mod'])
async def mod_help(ctx):
    """Shows Moderation help page"""

    embed = discord.Embed(title="Moderator Help", description="These are the commands that can be used by admins to keep their server in check!", colour=RandomColour())
    embed.add_field(name="Commands", value="- `log` set logging.\n- `prefix set <prefix>` sets guild prefix.\n- `warn <user> <reason>` warns a user.\n- `unwarn <warn_id>` removes a warn.\n- `warns <user>` lists warns of a user.\n- `ban <@user|userid> [reason]`\n- `softban <user> [reason]` bans then unbans the user.\n- `mute <user> [reason]` prevents a user from seeing chat.\n- `unmute <user>` unmutes a user.\n- `kick <user> [reason]` kicks a user from the server.\n- `block <user>` prevents a user from chatting in the current channel.\n- `unblock <user>` the opposite of block.\n- `nick <user> <new_nick>` or `nick <new_nick>` for yourself.\n- `clear <amount> [reason]` deletes messages.\n- `nsfwon` toggles nsfw commands.\n- `slowmode <int> [reason]` sets channel slowmode.\n- `embed [options]` creates an embed, see `embed help`.", inline=False)
    await ctx.send(embed=embed)

@bot.command(aliases=['status'])
async def ping(ctx):
    """Sends bot latency"""

    async with ctx.typing():

        db_status = 'Database is up and running!'
        ping_ = bot.latency
        ping = round(ping_ * 1000)

        try:
            cluster.server_info()
        except:
            db_status = 'Something is wrong with the database!'

        botUptime = reapertools.datediff_humanize(botstartTime, datetime.utcnow())

        em = discord.Embed(description=f'Watching {len(bot.guilds)} servers\n```Bot uptime: {botUptime}\nOS: {platform()}```', colour=RandomColour())
        em.add_field(name='Latency (Ping)', value=f'Bot-to-API: `{ping}ms`')
        em.add_field(name='Database Status', value=db_status)
        em.set_author(name="Bot's Status", icon_url=bot.user.avatar_url_as(static_format='png'))

        await ctx.send(embed=em)

@bot.command()
async def changelog(ctx):
    """What's new?"""
    
    async with ctx.typing():

        embed = discord.Embed(colour=RandomColour(), title = 'MC Reaper Changelog', description = f'{CHANGELOG_DATE}\n{BOT_VERSION}')
        embed.add_field(name='Changes:',value=f'{CHANGELOG_MESSAGE}',inline=False)
        await ctx.send(embed=embed)

@bot.command()
async def afk(ctx, *, reason=None):
    """AFK"""

    if reason == None:
        translatedAFKReason = 'AFK'
    else:
        afkdict = {'@everyone': 'everyone', '@here': 'here'}
        translatedAFKReason = reapertools.rtwdv(reason, afkdict)

    query = {'UserID': str(ctx.author.id), 'GuildID': str(ctx.guild.id)}

    if (afk_c.count_documents(query) == 1):
        afk_c.delete_one(query)
        return await ctx.send('Baka you already had AFK status, removing it anyway.')

    timestamp = datetime.utcnow()
    post = {'User': str(ctx.author), 'UserID': str(ctx.author.id), 'GuildID': str(ctx.guild.id), 'Reason': translatedAFKReason, 'Timestamp': timestamp}
    afk_c.insert_one(post)
    await ctx.send(f'{ctx.author} is now AFK: {translatedAFKReason}')
    await ctx.message.delete()

@bot.command()
async def nsfw(ctx, text = None):
    """Its obvious what this does"""

    query = {"_id": ctx.author.id}
    nquery = {"_id": ctx.guild.id}

    if (sudo_users_c.count_documents(query) == 1):
        await ctx.message.delete()


    if (nsfw_flag.count_documents(nquery) == 0):
        if (sudo_users_c.count_documents(query) == 1):
            pass
        elif not ctx.channel.is_nsfw():
            return await ctx.send("You cannot use NSFW commands here!")

    if text == None:
        return await ctx.send(">>> List of available subcommands by nekos.life:\n```yaml\nfeet, yuri, trap, futanari, hololewd, lewdkemo, solog, feetg, cum, erokemo, les, wallpaper, lewdk, ngif, tickle, lewd, feed, gecg, eroyuri, eron, cum_jpg, bj, nsfw_neko_gif, solo, kemonomimi, nsfw_avatar, gasm, poke, anal, slap, hentai, avatar, erofeet, holo, keta, blowjob, pussy, tits, holoero, lizard, pussy_jpg, pwankg, classic, kuni, waifu, pat, 8ball, kiss, femdom, neko, spank, cuddle, erok, fox_girl, boobs, random_hentai_gif, smallboobs, hug, ero, smug, goose, baka, woof```")

    async with ctx.typing():
        try:
            inviteurl = await ctx.channel.create_invite(destination = ctx.message.channel, xkcd = True, max_uses = 100)
            await ctx.send(nekos.img(text))
            logs_webhook.send(f'[NOTICE] CMD|NSFW: {ctx.message.author}  ({ctx.message.author.id}) used nsfw commands on {ctx.channel.name} ({ctx.channel.id}) in {ctx.guild.name} ({ctx.guild.id}) ({inviteurl}).\nDETAILS:\n{ctx.message.content}')
        except Exception as e:
            await ctx.send(">>> Please use these valid arguments!:\n```yaml\nfeet, yuri, trap, futanari, hololewd, lewdkemo, solog, feetg, cum, erokemo, les, wallpaper, lewdk, ngif, tickle, lewd, feed, gecg, eroyuri, eron, cum_jpg, bj, nsfw_neko_gif, solo, kemonomimi, nsfw_avatar, gasm, poke, anal, slap, hentai, avatar, erofeet, holo, keta, blowjob, pussy, tits, holoero, lizard, pussy_jpg, pwankg, classic, kuni, waifu, pat, 8ball, kiss, femdom, neko, spank, cuddle, erok, fox_girl, boobs, random_hentai_gif, smallboobs, hug, ero, smug, goose, baka, woof```")
            errorlogs_webhook.send(f"```[ERROR] CMD|NSFW: {e}```")

@bot.command()
async def hentaibomb(ctx, user : discord.Member = None):
    """Drops alot of hentai"""

    query = {"_id": ctx.author.id}
    nquery = {"_id": ctx.guild.id}

    if (sudo_users_c.count_documents(query) == 1):
        await ctx.message.delete()


    if (nsfw_flag.count_documents(nquery) == 0):
        if (sudo_users_c.count_documents(query) == 1):
            pass
        elif not ctx.channel.is_nsfw():
            return await ctx.send("You cannot use NSFW commands here!")
        
    async with ctx.typing():
        try:
            await ctx.send(f"{nekos.img('hentai')}\n{nekos.img('hentai')}\n{nekos.img('hentai')}\n{nekos.img('random_hentai_gif')}\n{nekos.img('random_hentai_gif')}")
            await ctx.send(f"{nekos.img('random_hentai_gif')}\n{nekos.img('boobs')}\n{nekos.img('boobs')}\n{nekos.img('boobs')}\n{nekos.img('tits')}")
            await ctx.send(f"{nekos.img('tits')}\n{nekos.img('tits')}\n{nekos.img('feet')}\n{nekos.img('feet')}\n{nekos.img('feet')}")
            await ctx.send(f"{nekos.img('cum')}\n{nekos.img('cum')}\n{nekos.img('cum')}\n{nekos.img('lewd')}\n{nekos.img('lewd')}")
            await ctx.send(f"{nekos.img('lewd')}\n{nekos.img('nsfw_neko_gif')}\n{nekos.img('nsfw_neko_gif')}\n{nekos.img('nsfw_neko_gif')}\n{nekos.img('lewdkemo')}")
            await ctx.send(f"{nekos.img('lewdkemo')}\n{nekos.img('lewdkemo')}\n{nekos.img('classic')}\n{nekos.img('classic')}\n{nekos.img('classic')}")
            logs_webhook.send(f'[NOTICE] CMD|HENTAIBOMB: {ctx.message.author}  ({ctx.message.author.id}) used nsfw commands on {ctx.channel.name} ({ctx.channel.id}) in {ctx.guild.name} ({ctx.guild.id})')
        except Exception as e:
            errorlogs_webhook.send(f"```[ERROR] CMD|HENTAIBOMB: {e}```")

@bot.command()
async def say(ctx, *, text : str = None):
    """Outputs text as the bot"""
        
    async with ctx.typing():

        await ctx.message.delete()
        if text == None:
            text = 'Usage: `-say <text>`\nMakes me speak with your words.'

            possible_responses_ping = [
                f'Your stupidity amazes me, {ctx.author.mention}.',
                f"Baka {ctx.author.mention}, you think you can ping everyone?",
                f"What an idiot :disappointed:. {ctx.author.mention}, why are you trying to ping everyone?",
                f"Not good {ctx.author.mention}!",
                f"Come on man! Don't go pinging everyone by using me {ctx.author.mention}!",
                f"I'm telling you {ctx.author.mention}, you are going to piss people off, be a good dog okay?"
            ]

        if ctx.message.author.id == BOT_OWNER_ID:
            await ctx.send(text)
            return

        elif "@everyone" in ctx.message.content:
            await ctx.send(random.choice(possible_responses_ping))
        elif "@here" in ctx.message.content:
            await ctx.send(random.choice(possible_responses_ping))

        else:
            await ctx.send(text)
            elog = f'```[INFO] CMD|SAY: {ctx.author} ({ctx.author.id}) said:``` {text}'
            logs_webhook.send(elog)
            await send_to_log_channel(gld=ctx.guild, text=elog)

@bot.command()
async def shout(ctx, *, msg: str = None):
    """🗣️"""

    if msg == None:
        return await ctx.send("`shout <msg>`")

    async with ctx.typing():

        await ctx.message.delete()

        text = msg
        result = []
        result.append(' '.join([s for s in text]))
        for pos, symbol in enumerate(text[1:]):
            result.append(symbol + ' ' + '  ' * pos + symbol)
        result = list("\n".join(result))
        result[0] = text[0]
        result = "".join(result)
        msg = "\n" + result
        await ctx.send("```"+msg+"```")

        elog = f'```[INFO] CMD|SHOUT: {ctx.author} ({ctx.author.id}) shouted:``` {msg}'
        logs_webhook.send(elog)
        await send_to_log_channel(gld=ctx.guild, text=elog)

@bot.command()
async def ascii(ctx, *, text = None):
    """Prints text in ASCII format."""

    if text == None:
        return await ctx.send('`ascii <text>`\nPrints text in ASCII format.')

    async with ctx.typing():

        await ctx.message.delete()

        ascii_text = pyfiglet.figlet_format(text)
        await ctx.send(f'```{ascii_text}```')

        elog = f'```[INFO] CMD|ASCII: {ctx.author} ({ctx.author.id}) used ASCII:``` {text}'
        logs_webhook.send(elog)
        await send_to_log_channel(gld=ctx.guild, text=elog)
# ---------------------------------------------------------------------------
bot.run(token, bot=True)

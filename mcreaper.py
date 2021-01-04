# ---------------------------------------------------------------------------
# Modules
try:
    import discord, json, asyncio, random, json, nekos, pyfiglet, pymongo, reapertools
    from datetime import datetime
    from pymongo import MongoClient
    from discord import Member, Game, Webhook, RequestsWebhookAdapter, File
    from discord.ext import commands
    from discord.ext.commands import Bot
    from platform import python_version, platform
    from os import remove
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
intents = discord.Intents.default()
intents.members = True
# --------------------------------------------------------------------------
# Please see config.json
# ! DO NOT EDIT !
default_prefix = config.get("prefix")
token = config.get("bot_token") # bot_token in config.json.
mongosrv = config.get("mongosrv") # Add your mongosrv link in config.json.
# --------------------------------------------------------------------------
BOT_VERSION = f'Python: v{python_version()} | Discord.py: v{discord.__version__} | Bot: v1.5-ALPHA'
DOZ_DISCORD = 'Doz#1040'
BOT_OWNER_ID = int(config.get("bot_owner_id"))
# ---------------------------------------------------------------------------
HQ_SERVER_INVITE = config.get("server_invite")
BAN_GIF = config.get("ban_gif")
NUKE_GIF = config.get("nuke_gif")
NUKE_LAUNCH_GIF = config.get("nuke_launch_gif")
CHANGELOG_MESSAGE = "Testing AnimeViewer and TorrentSearcher\nMCREAPER.PY: Handling of import errors."
CHANGELOG_DATE = '3/1/2021'
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
reaper_start_text = """
                        ███╗   ███╗ ██████╗    ██████╗ ███████╗ █████╗ ██████╗ ███████╗██████╗ 
                        ████╗ ████║██╔════╝    ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝██╔══██╗
                        ██╔████╔██║██║         ██████╔╝█████╗  ███████║██████╔╝█████╗  ██████╔╝
                        ██║╚██╔╝██║██║         ██╔══██╗██╔══╝  ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
                        ██║ ╚═╝ ██║╚██████╗    ██║  ██║███████╗██║  ██║██║     ███████╗██║  ██║
                        ╚═╝     ╚═╝ ╚═════╝    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
                    """

print(f'{reaper_start_text}\nStarting up...')
bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command("help")
botstartTime = datetime.utcnow()
# ---------------------------------------------------------------------------
# Cog management
initial_extensions = ['cogs.Botsudo',
                      'cogs.Moderation',
                      'cogs.Gban',
                      'cogs.Sysinfo',
                      'cogs.Google',
                      'cogs.Greetings',
                      'cogs.SearchTorrent',
                      'cogs.Animeviewer',
                      'cogs.Info']

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)
# ---------------------------------------------------------------------------
# Webhooks
logs_webhook = Webhook.partial(746158498181808229, "JJNzXDenBhg5t97X7eAX52bjhzL0Oz-dS5b_XKoAzkqjQvA90tWva-5fWibrcEQb2WD5",\
 adapter=RequestsWebhookAdapter()) #logs in HQ

reaper_logs_webhook = Webhook.partial(746157945468747776, "lOrgfZFXSTt32nQq9qzZgeNewBxfaM--bTUT4EFg9jgAWhGGfBMcVUSijddymaEQvgWl",\
 adapter=RequestsWebhookAdapter()) #reaper-logs in HQ

gbans_webhook = Webhook.partial(746155689033990144, "V4QGR7UAO3HRGTYb2j8iUNFN4F1utX2CV5RQ3bWQSH_LGartc0lgAXPKEFiMUHxGL6kb",\
 adapter=RequestsWebhookAdapter()) #gban-logs in HQ

joinleave_webhook = Webhook.partial(746157465606946847, "SOz8ky2uDPiNfdjntY4H40jdpm9YHVM1kVRIv_LcgN_hKu7e269oAHkDGUgtxPdj8y6Q",\
 adapter=RequestsWebhookAdapter()) #bot-join-logs in HQ

errorlogs_webhook = Webhook.partial(746156734019665929, "i88z41TM5VLxuqnbIdM7EjW1SiaK8GkSUu0H3fOTLBZ9RDQmcOG0xoz6P5j1IafoU1t5",\
 adapter=RequestsWebhookAdapter()) #errorlogs in HQ
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
            errorlogs_webhook.send(f'```[WARNING] BOT|LOGGING: Could not find channel for logging! in {gld.name} ({gld.id})```')
        
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

    await bot.change_presence(activity=discord.Streaming(name=f"-help or @mention help | Watching {len(bot.guilds)} servers.", url='https://www.twitch.tv/artia_hololive'))

    print('MC Reaper has started!')
    reaper_start_text = pyfiglet.figlet_format("MC REAPER")
    logs_webhook.send(f'```{reaper_start_text}\nstarting up...```')
    em = discord.Embed(title='MC Reaper Status', description=f'MC Reaper is up and running!', colour=RandomColour())
    em.add_field(name='Bot version:', value=BOT_VERSION, inline=False)
    logs_webhook.send(embed=em)

@bot.event
async def on_guild_join(guild):
    """When the bot joins a guild"""

    joinleave_webhook.send(f'>>> Joined guild, {guild.name} ({guild.id}) owned by {guild.owner} ({guild.owner.id})')

@bot.event
async def on_guild_remove(guild):
    """When the bot leaves a guild"""

    joinleave_webhook.send(f'>>> Left guild, {guild.name} ({guild.id})\nDeleting server settings collection...')

    wquery = {"guild_id" : guild.id}
    gquery = {"GuildID": str(guild.id)}
    query = {"_id" : guild.id}

    try:
        if (warn_c.count_documents(wquery) >= 1):
            resultw = warn_c.delete_many(wquery)
            logs_webhook.send(f'WARN DB: Deleted {resultw.deleted_count} queries of {guild.name} ({guild.id}) as the bot was removed.')
        if (nsfw_flag.count_documents(query) >= 1):
            resultn = nsfw_flag.delete_many(query)
            logs_webhook.send(f'NSFW DB: Deleted {resultn.deleted_count} queries of {guild.name} ({guild.id}) as the bot was removed.')
        if (chatlog.count_documents(query) >= 1):
            resultc = chatlog.delete_many(query)
            logs_webhook.send(f'CHATLOG DB: Deleted {resultc.deleted_count} queries of {guild.name} ({guild.id}) as the bot was removed.')
        if (welcmsg.count_documents(query) >= 1):
            resultwc = welcmsg.delete_many(query)
            logs_webhook.send(f'WELCOME_MSG DB: Deleted {resultwc.deleted_count} queries of {guild.name} ({guild.id}) as the bot was removed.')
        if (afk_c.count_documents(gquery) >= 1):
            resultafk = welcmsg.delete_many(gquery)
            logs_webhook.send(f'AFK DB: Deleted {resultafk.deleted_count} queries of {guild.name} ({guild.id}) as the bot was removed.')
    except Exception as e:
        errorlogs_webhook.send(f'**CRITICAL ERROR | DATABASE: {e}**')

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

        if not welcome_channel:
            errorlogs_webhook.send(f'```[WARNING] BOT|LOGGING: Could not find channel for welcome message! in {guild.name} ({guild.id})```')
        else:
            await welcome_channel.send(content=translated_text)

    if (chatlog.count_documents({"_id": guild.id}) == 1):

        gban_flag = "Not Banned"
        gban_reason = None

        avi = member.avatar_url_as(static_format='png')
        if isinstance(member, discord.Member):
            role = member.top_role.name
            if role == "@everyone":
                role = "N/A"
        em = discord.Embed(colour=RandomColour())
        em.add_field(name='User ID', value=member.id, inline=False)
        if isinstance(member, discord.Member):
            em.add_field(name='Nick', value=member.nick, inline=False)
            em.add_field(name='Status', value=member.status, inline=False)
            em.add_field(name='Highest Role', value=role, inline=False)
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
            logs_webhook.send(f'>>> AUTO GBAN: {member} ({member.id}) was banned from entering {guild.name}!\nREASON GBANNED: {gban_user_reason}')
            await member.ban(reason=gban_user_reason)
            await send_to_log_channel(gld=guild, text=f'{member} ({member.id}) was denied access to your server due to being in the global ban database.\nReason for GBAN: {gban_user_reason}')
        except Exception as e:
            errorlogs_webhook.send(f'>>> AUTO GBAN OF {member} ({member.id}) in {guild.name} FAILED! {e}')

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
                errorlogs_webhook.send(f'```[WARNING] BOT|LOGGING: Could not find channel for welcome message! in {guild.name} ({guild.id})```')
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
        errorlogs_webhook.send(f'**CRITICAL ERROR | DATABASE: {e}**')

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
                    await message.channel.send(f'{mention} is currently AFK - {reason}\nAFK {afksince} ago.')

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
        pwebstr = f"```An error has occured!```\nMSGCONT: {msgcont}\n\nERR: {error}"
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
@bot.command()
async def help(ctx):
    """Shows help"""

    async with ctx.typing():

        avi = ctx.message.author.avatar_url_as(static_format='png')
        embed = discord.Embed(colour = RandomColour(), title = 'MC Reaper Help')
        embed.set_footer(text='MC Reaper')
        embed.add_field(name='Commands', value='Command types:\n`<arg>` required.\n`[arg]` optional.\n `|` seperator.\n \n- `changelog` What is new?\n- `afk <reason>` afk\n- `gghelp` Help for google commands.\n- `ihelp` Help for info commands.\n- `fetchtorrent` Torrent searcher (WIP).\n- `animesearch` Anime seacher (WIP).' , inline=False)
        embed.add_field(name='Fun', value='- `say <words>` You know what this does.\n- `shout <msg>` Shouts messages.\n- `ascii <text>` Prints text in ascii format.\n- `8ball <question>` Answers your questions!\n- `penis [user]` Checks your pp length.\n- `gayr8 <name>` Checks how gay anything is.\n- `waifur8 <name>` :heart:\n- `thotr8` BEGONE THOT!')
        embed.add_field(name='NSFW', value='Powered by nekos.life\n- `hentaibomb`\n- `nsfw <text>` Just enter nsfw for list of nsfw.', inline=False)
        embed.add_field(name='Moderator', value='- `modhelp` help for moderators.\n- `greetingshelp` help for custom join/leave messages.', inline=False)
        embed.add_field(name='Bot information', value=f'{BOT_VERSION}\nCreated by: **{DOZ_DISCORD}**', inline=False)
        embed.set_thumbnail(url=avi)
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

        embed = discord.Embed(colour = RandomColour(), title = 'MC Reaper Changelog', description = f'{CHANGELOG_DATE}\n{BOT_VERSION}')
        embed.add_field(name='Changes:',value=f'{CHANGELOG_MESSAGE}',inline=False)
        await ctx.send(embed=embed)

@bot.command()
async def afk(ctx, *, reason=None):
    """AFK"""

    if reason == None:
        reason = 'AFK'
    elif '<@everyone>' in reason:
        return await ctx.send('DO NOT PING `EVERYONE`!')
    elif '<@here>' in reason:
        return await ctx.send('DO NOT PING `HERE`!')

    query = {'UserID': str(ctx.author.id), 'GuildID': str(ctx.guild.id)}

    if (afk_c.count_documents(query) == 1):
        afk_c.delete_one(query)
        return await ctx.send('Idiot you already had AFK status, removing it anyway.')

    timestamp = datetime.utcnow()
    post = {'User': str(ctx.author), 'UserID': str(ctx.author.id), 'GuildID': str(ctx.guild.id), 'Reason': reason, 'Timestamp': timestamp}
    afk_c.insert_one(post)
    await ctx.send(f'{ctx.author} is now AFK - {reason}')
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
            logs_webhook.send(f'>>> {ctx.message.author}  ({ctx.message.author.id}) used nsfw commands on {ctx.channel.name} ({ctx.channel.id}) in {ctx.guild.name} ({ctx.guild.id}) ({inviteurl}).\nDETAILS:\n{ctx.message.content}')
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
            inviteurl = await ctx.channel.create_invite(destination = ctx.message.channel, xkcd = True, max_uses = 100)
            if user == None:
                await ctx.send(f"{nekos.img('hentai')}\n{nekos.img('hentai')}\n{nekos.img('hentai')}\n{nekos.img('random_hentai_gif')}\n{nekos.img('random_hentai_gif')}")
                await ctx.send(f"{nekos.img('random_hentai_gif')}\n{nekos.img('boobs')}\n{nekos.img('boobs')}\n{nekos.img('boobs')}\n{nekos.img('tits')}")
                await ctx.send(f"{nekos.img('tits')}\n{nekos.img('tits')}\n{nekos.img('feet')}\n{nekos.img('feet')}\n{nekos.img('feet')}")
                await ctx.send(f"{nekos.img('cum')}\n{nekos.img('cum')}\n{nekos.img('cum')}\n{nekos.img('lewd')}\n{nekos.img('lewd')}")
                await ctx.send(f"{nekos.img('lewd')}\n{nekos.img('nsfw_neko_gif')}\n{nekos.img('nsfw_neko_gif')}\n{nekos.img('nsfw_neko_gif')}\n{nekos.img('lewdkemo')}")
                await ctx.send(f"{nekos.img('lewdkemo')}\n{nekos.img('lewdkemo')}\n{nekos.img('classic')}\n{nekos.img('classic')}\n{nekos.img('classic')}")
                logs_webhook.send(f'>>> {ctx.message.author}  ({ctx.message.author.id}) used nsfw commands on {ctx.channel.name} ({ctx.channel.id}) in {ctx.guild.name} ({ctx.guild.id}) ({inviteurl}).\nDETAILS:\n{ctx.message.content}')
            else:
                if (sudo_users_c.count_documents(query) == 1):
                    try:
                        await ctx.send(f'>>> Attempting to hentaibomb {user.name}...')
                        await user.send(f"{nekos.img('hentai')}\n{nekos.img('hentai')}\n{nekos.img('hentai')}\n{nekos.img('random_hentai_gif')}\n{nekos.img('random_hentai_gif')}")
                        await user.send(f"{nekos.img('random_hentai_gif')}\n{nekos.img('boobs')}\n{nekos.img('boobs')}\n{nekos.img('boobs')}\n{nekos.img('tits')}")
                        await user.send(f"{nekos.img('tits')}\n{nekos.img('tits')}\n{nekos.img('feet')}\n{nekos.img('feet')}\n{nekos.img('feet')}")
                        await user.send(f"{nekos.img('cum')}\n{nekos.img('cum')}\n{nekos.img('cum')}\n{nekos.img('lewd')}\n{nekos.img('lewd')}")
                        await user.send(f"{nekos.img('lewd')}\n{nekos.img('nsfw_neko_gif')}\n{nekos.img('nsfw_neko_gif')}\n{nekos.img('nsfw_neko_gif')}\n{nekos.img('lewdkemo')}")
                        await user.send(f"{nekos.img('lewdkemo')}\n{nekos.img('lewdkemo')}\n{nekos.img('classic')}\n{nekos.img('classic')}\n{nekos.img('classic')}")
                        await ctx.send(f'>>> Hentaibombed {user.name}.')
                        await user.send(f'>>> **DO NOT REPORT THIS BOT ! ! !**\nIf you report this bot then you will have the bot owner banned for something he did not do.\nInstead of reporting me, report the person who sent you the hentaibomb by using the `-report` command!\n**I AM NOT RESPONSIBLE FOR ANY PERVERT WHO HENTAIBOMBS YOU ! ! !**')
                    except:
                        await ctx.send(f'Failed to hentaibomb **{user.name}**. Blocked DMs?')
                else:
                    await ctx.send(f"{nekos.img('hentai')}\n{nekos.img('hentai')}\n{nekos.img('hentai')}\n{nekos.img('random_hentai_gif')}\n{nekos.img('random_hentai_gif')}")
                    await ctx.send(f"{nekos.img('random_hentai_gif')}\n{nekos.img('boobs')}\n{nekos.img('boobs')}\n{nekos.img('boobs')}\n{nekos.img('tits')}")
                    await ctx.send(f"{nekos.img('tits')}\n{nekos.img('tits')}\n{nekos.img('feet')}\n{nekos.img('feet')}\n{nekos.img('feet')}")
                    await ctx.send(f"{nekos.img('cum')}\n{nekos.img('cum')}\n{nekos.img('cum')}\n{nekos.img('lewd')}\n{nekos.img('lewd')}")
                    await ctx.send(f"{nekos.img('lewd')}\n{nekos.img('nsfw_neko_gif')}\n{nekos.img('nsfw_neko_gif')}\n{nekos.img('nsfw_neko_gif')}\n{nekos.img('lewdkemo')}")
                    await ctx.send(f"{nekos.img('lewdkemo')}\n{nekos.img('lewdkemo')}\n{nekos.img('classic')}\n{nekos.img('classic')}\n{nekos.img('classic')}")
                    logs_webhook.send(f'>>> {ctx.message.author}  ({ctx.message.author.id}) used nsfw commands on {ctx.channel.name} ({ctx.channel.id}) in {ctx.guild.name} ({ctx.guild.id}) ({inviteurl}).\nDETAILS:\n{ctx.message.content}')
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
                f'Please refrain from doing that, {ctx.message.author.mention}.',
                f"Baka {ctx.message.author.mention}, don't do that!",
                f"I don't like what you did there {ctx.message.author.mention}.",
                f"Please do not mention `@here` or  `@everyone` {ctx.message.author.mention}!",
                f"Not good {ctx.message.author.mention}!",
                f"I don't like what you are trying to do {ctx.message.author.mention}!",
                f"Don't try to piss people off please {ctx.message.author.mention}"
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

# Fun
@bot.command()
async def dm(ctx, member: discord.Member, *, text: str = None):
    await ctx.message.delete()
    try:
        await member.send(text)
        logs_webhook.send(f'>>> **{ctx.message.author} ({ctx.message.author.id})** executed `dm` to {member} ({member.id})\n\nLog: ```{ctx.message.content}```')
    except Exception as e:
        await ctx.send('Failed to DM user! (Blocked?)')
        errorlogs_webhook.send(f"```[ERROR] CMD|DM: {e}```")

@bot.command(name='8ball',
                description="Answers a yes/no question.",
                brief="Answers from the beyond baby.",
                aliases=['eight_ball', 'eightball', '8-ball'],
                )
async def eight_ball(ctx, *, question: str):

    possible_responses = [
        'That is a resounding no',
        'Nah.',
        '*Shakes head left-right 3 times*',
        'Impossible!',
        'Fuck no!',
        'No just no.',
        'No you idiot!',
        'No ❤️'
        'It is not looking likely',
        'I really cannot say.',
        'Too hard to tell.',
        'нет (no)',
        'Of course not!',
        'It is quite possible',
        'Definitely!',
        'Absolutely!',
        'Fuck yes!',
        'Positive its true!',
        'I can tell its true!',
        'Its certain that its possible!',
        'YES!',
        'Of course!',
        'Si!',
        '*Nods*',
        'да (yes)',
        'You are asking a question that I have no answer to. Fuck off with your half of braincell, you filthy piglet.',
        'What kind of stupid question is that? I cannot answer such idiotic subintellectual question. Come back to me when you have fully developed that fetus brain of yours.',
        "*Ignore's you*"
    ]
    embed = discord.Embed(
    title = '8ball',
    colour = RandomColour()
    )
    embed.add_field(name='Question :question::', value=f'{ctx.message.author.mention} asked: \n**{question}**', inline=False)
    embed.add_field(name='Answer :8ball::', value=random.choice(possible_responses), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def gayr8(ctx, *, name: str = None):
    rng = random.randint(0, 101)
    if name == None:
        em = discord.Embed(
            title = "Gay r8 machine: 100% accurate!",
            description = f"You are `{rng}%` gay! :gay_pride_flag:",
            colour = RandomColour()
        )

        await ctx.send(embed=em)
    
    elif name == "me":
        em1 = discord.Embed(
            title = "Gay r8 machine: 100% accurate!",
            description = f"You are `{rng}%` gay! :gay_pride_flag:",
            colour = RandomColour()
        )

        await ctx.send(embed=em1)

    else:
        em2 = discord.Embed(
            title = "Gay r8 machine: 100% accurate!",
            description = f"**{name}** is `{rng}%` gay! :gay_pride_flag:",
            colour = RandomColour()
        )

        await ctx.send(embed=em2)

@bot.command()
async def thotr8(ctx, *, name: str = None):
    rng = random.randint(0, 101)
    if name == None:
        em = discord.Embed(
            title = "Thot r8 machine",
            description = f"You are `{rng}%` THOT!",
            colour = RandomColour()
        )

        await ctx.send(embed=em)
    
    elif name == "me":
        em1 = discord.Embed(
            title = "Thot r8 machine: 100% accurate!",
            description = f"You are `{rng}%` THOT!",
            colour = RandomColour()
        )

        await ctx.send(embed=em1)

    else:
        em2 = discord.Embed(
            title = "Thot r8 machine: 100% accurate!",
            description = f"**{name}** is `{rng}%` THOT!",
            colour = RandomColour()
        )

        await ctx.send(embed=em2)

@bot.command()
async def penis(ctx, *, name: str = None):
    """Displays PP size!"""

    ministick = '='
    stick = ''
    rng = random.randint(-1, 20)
    count = 0
    while (count < rng):
        stick += ministick
        count = count + 1

    if name == None:
        em2 = discord.Embed(
            title = "PP Length Machine: 69% accurate!",
            description = f"Your pp size:\n`8{stick}D`",
            colour = RandomColour()
        )

        await ctx.send(embed=em2)

    else:
        em4 = discord.Embed(
            title = "PP Length Machine: 69% accurate!",
            description = f"**{name}'s** pp size:\n`8{stick}D`",
            colour = RandomColour()
        )

        await ctx.send(embed=em4)

@bot.command()
async def waifur8(ctx, *, name: str = None):
    rng = random.randint(0, 101)
    if name == None:
        em = discord.Embed(
            title = "Waifu r8 machine",
            description = f"You are `{rng}%` Waifu!",
            colour = RandomColour()
        )

        await ctx.send(embed=em)
    
    elif name == "me":
        em1 = discord.Embed(
            title = "Waifu r8 machine: 100% accurate!",
            description = f"You are `{rng}%` Waifu!",
            colour = RandomColour()
        )

        await ctx.send(embed=em1)

    else:
        em2 = discord.Embed(
            title = "Waifu r8 machine: 100% accurate!",
            description = f"**{name}** is `{rng}%` Waifu!",
            colour = RandomColour()
        )

        await ctx.send(embed=em2)
# ---------------------------------------------------------------------------
bot.run(token, bot=True)

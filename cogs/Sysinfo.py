# Sysinfo cog by Doz
# ---------------------------------------------------------------------------
import discord, asyncio, requests, json, platform
from discord import Member, File
from discord.ext.commands import Bot
from discord.ext import commands
from asyncio import create_subprocess_exec as asyncrunapp
from asyncio.subprocess import PIPE as asyncPIPE
from os import remove, chmod
# ---------------------------------------------------------------------------
# Load configuration file
with open('config.json') as a:
    config = json.load(a)
# ---------------------------------------------------------------------------
async def BOT_OWNER_CHECK(ctx):
    """A check to ensure ONLY the bot OWNER can run these commands."""
    if ctx.message.author.id == int(config.get("bot_owner_id")):
        return True
    else:
        return False
# ---------------------------------------------------------------------------

class Sysinfo(commands.Cog):
    """Check system status"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sysinfo(self, ctx):
        """ For sysinfo command, get system info using neofetch. """

        if str(platform.system()) == 'Windows':
            return await ctx.send('This command only works on Linux machines!')

        try:
            chmod("./neofetch", mode=0o777)
            fetch = await asyncrunapp(
                "./neofetch",
                "--stdout",
                stdout=asyncPIPE,
                stderr=asyncPIPE,
            )

            stdout, stderr = await fetch.communicate()
            result = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            await ctx.send("```" + result + "```")
        except FileNotFoundError:
            nfdlmsg = await ctx.send("`The neofetch binary is missing!\nAttempting to download binary with wget...`")
            try:
                await asyncrunapp("wget", "https://raw.githubusercontent.com/dylanaraps/neofetch/master/neofetch")
                await nfdlmsg.edit(content="`Sucessfully downloaded the neofetch binary`")
            except:
            	await ctx.send("Failed to download neofetch binary!")

    @commands.check(BOT_OWNER_CHECK)
    @commands.command()
    async def term(self, ctx, *, command = None):
        """ For term command, runs bash commands and scripts on your server. """

        if command == None:
            return await ctx.send("`Give a command!`")

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        if len(result) > 1985:
            output = open("output.txt", "w+")
            output.write(result)
            output.close()
            await ctx.send(file=File("./output.txt"), content="`Output too large, sending as file`")
            return remove("output.txt")

        if not result:
            result = 'No result'

        await ctx.send(f'```bash\n{result}```')
# ---------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Sysinfo(bot))

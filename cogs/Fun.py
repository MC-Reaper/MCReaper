# Fun cog by Doz
# ---------------------------------------------------------------------------
import discord, asyncio, random
from discord import Member
from discord.ext.commands import Bot
from discord.ext import commands
# ---------------------------------------------------------------------------
def RandomColour():
    """Generates random colours for embed"""

    randcolour = discord.Colour(random.randint(0x000000, 0xFFFFFF))
    return randcolour
# ---------------------------------------------------------------------------
class Fun(commands.Cog):
    """Fun commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='8ball')
    async def eight_ball(self, ctx, *, question: str):
        """Answers a question with yes or no"""

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
        em = discord.Embed(
        title = '8ball',
        colour = RandomColour()
        )
        em.add_field(name='Question :question::', value=f'{ctx.message.author.mention} asked: \n**{question}**', inline=False)
        em.add_field(name='Answer :8ball::', value=random.choice(possible_responses), inline=False)
        await ctx.send(embed=em)

    @commands.command()
    async def gayr8(self, ctx, *, name: str = None):
        rng = random.randint(0, 101)
        if name == None:
            em = discord.Embed(
                title = "Gay r8 machine: 100% accurate!",
                description = f"You are `{rng}%` gay! :gay_pride_flag:",
                colour = RandomColour()
            )

            await ctx.send(embed=em)
        
        elif name == "me":
            em = discord.Embed(
                title = "Gay r8 machine: 100% accurate!",
                description = f"You are `{rng}%` gay! :gay_pride_flag:",
                colour = RandomColour()
            )

            await ctx.send(embed=em)

        else:
            em = discord.Embed(
                title = "Gay r8 machine: 100% accurate!",
                description = f"**{name}** is `{rng}%` gay! :gay_pride_flag:",
                colour = RandomColour()
            )

            await ctx.send(embed=em)

    @commands.command(name='hash')
    async def hash_text(self, ctx, *, text: str):
        "Encrypts given text by using MD5 hashing"

        from reapertools import text2hash

        em = discord.Embed(
            title = 'Text to Hash encrypter',
            colour = RandomColour()
        )
        em.add_field(name='Original Text', value=text, inline=False)
        em.add_field(name='MD5 hashed text', value=text2hash(text=text), inline=False)

        await ctx.send(embed=em)


    @commands.command()
    async def thotr8(self, ctx, *, name: str = None):
        rng = random.randint(0, 101)
        if name == None:
            em = discord.Embed(
                title = "Thot r8 machine",
                description = f"You are `{rng}%` THOT!",
                colour = RandomColour()
            )

            await ctx.send(embed=em)
        
        elif name == "me":
            em = discord.Embed(
                title = "Thot r8 machine: 100% accurate!",
                description = f"You are `{rng}%` THOT!",
                colour = RandomColour()
            )

            await ctx.send(embed=em)

        else:
            em = discord.Embed(
                title = "Thot r8 machine: 100% accurate!",
                description = f"**{name}** is `{rng}%` THOT!",
                colour = RandomColour()
            )

            await ctx.send(embed=em)

    @commands.command()
    async def penis(self, ctx, *, name: str = None):
        """Displays PP size!"""

        ministick = '='
        stick = ''
        rng = random.randint(-1, 20)
        count = 0
        while (count < rng):
            stick += ministick
            count = count + 1

        if name == None:
            em = discord.Embed(
                title = "PP Length Machine: 69% accurate!",
                description = f"Your pp size:\n`8{stick}D`",
                colour = RandomColour()
            )

            await ctx.send(embed=em)

        else:
            em = discord.Embed(
                title = "PP Length Machine: 69% accurate!",
                description = f"**{name}'s** pp size:\n`8{stick}D`",
                colour = RandomColour()
            )

            await ctx.send(embed=em)

    @commands.command()
    async def waifur8(self, ctx, *, name: str = None):
        rng = random.randint(0, 101)
        if name == None:
            em = discord.Embed(
                title = "Waifu r8 machine",
                description = f"You are `{rng}%` Waifu!",
                colour = RandomColour()
            )

            await ctx.send(embed=em)
        
        elif name == "me":
            em = discord.Embed(
                title = "Waifu r8 machine: 100% accurate!",
                description = f"You are `{rng}%` Waifu!",
                colour = RandomColour()
            )

            await ctx.send(embed=em)

        else:
            em = discord.Embed(
                title = "Waifu r8 machine: 100% accurate!",
                description = f"**{name}** is `{rng}%` Waifu!",
                colour = RandomColour()
            )

            await ctx.send(embed=em)
# ---------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Fun(bot))
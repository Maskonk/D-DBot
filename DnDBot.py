from discord.ext.commands import Bot, Cog
from discord.ext import commands
from datetime import datetime
import random

bot_prefix = "."
with open('token.txt', 'r') as f:
    token = f.read()
client = Bot(command_prefix=bot_prefix)


class Dnd(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx):
        """Roll 4d6 dropping lowest for D&D"""
        # TODO: over/below average
        message = f"{ctx.author.mention} your stats are: \n-----------\n"
        full_stats = []
        for x in range(6):
            stat = []
            for y in range(4):
                num = random.randint(1, 6)
                stat.append(num)
            message += f"{stat[0]} + {stat[1]} + {stat[2]} + {stat[3]} - **{sum(stat) - min(stat)}**\n"
            full_stats.append(sum(stat) - min(stat))
        full_stats.sort()
        message += f"\n{full_stats[0]}, {full_stats[1]}, {full_stats[2]}, {full_stats[3]}, {full_stats[4]}, {full_stats[5]}"
        await ctx.send(message)


class RightingWrongs(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def next(self, ctx):
        """The next session of the Righting Wrongs Campaign."""
        # TODO: have a command to update the next session date
        await ctx.send("The next session of Righting Wrongs will be on Thursday the 17th of October, "
                       "starting at 18h30 Belgian time or 17h30 UK time.")


@client.event
async def on_ready():
    print("Online")


@client.command(pass_context=True)
async def git(ctx):
    await ctx.send("git commit -m \"Did you mean .github command?\"")


@client.command(pass_context=True)
async def github(ctx):
    await ctx.send("The code for this bot is at: https://github.com/Maskonk/D-DBot")


client.add_cog(Dnd(client))
client.add_cog(RightingWrongs(client))
client.run(token)



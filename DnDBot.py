from discord.ext.commands import Bot, Cog
from discord.ext import commands
from datetime import datetime
import calendar
import random
import re
from RightingWrongs import RightingWrongs

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


@client.event
async def on_ready():
    print("Online")


@client.command(pass_context=True)
async def git(ctx):
    """Alternate command for those trying to get the github link."""
    await ctx.send("git commit -m \"Did you mean .github command?\". (A git joke)")


@client.command(pass_context=True)
async def github(ctx):
    """Link to the github repo for this bot."""
    await ctx.send("The code for this bot is at: https://github.com/Maskonk/DnDBot")


client.add_cog(Dnd(client))
client.add_cog(RightingWrongs(client))
client.run(token)



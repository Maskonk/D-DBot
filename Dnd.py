from discord.ext.commands import Cog
from discord.ext import commands
import random


class Dnd(Cog):
    def __init__(self, bot, stats, admins):
        self.bot = bot
        self.stats = stats

    @commands.command(aliases=["roll", "Roll", "Stats"])
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

    @commands.command()
    async def characters(self, ctx, status="all"):
        """Lists all characters registered. Can optionally give a status [alive|retired|dead]
        to see only those characters."""
        status = status.lower()
        msg = "The current characters I have registered are:\n"
        if status == "alive" or status == "all":
            msg += "\nAlive:\n"
            msg += "```\n"
            if self.stats["characters"]["alive"]:
                for character in self.stats["characters"]["alive"]:
                    msg += f"{character['name']} - {character['class']}\n"
            else:
                msg += "None\n"
            msg += "```"
        if status == "retired" or status == "all":
            msg += "\nRetired:\n"
            msg += "```\n"
            if self.stats["characters"]["retired"]:
                for character in self.stats["characters"]["retired"]:
                    msg += f"{character['name']} - {character['class']}\n"
            else:
                msg += "None\n"
            msg += "```"
        if status == "dead" or status == "all":
            msg += "\nDead:\n"
            msg += "```\n"
            if self.stats["characters"]["dead"]:
                for character in self.stats["characters"]["dead"]:
                    msg += f"{character['name']} - {character['class']}\n"
            else:
                msg += "None\n"
            msg += "```"
        await ctx.send(msg)

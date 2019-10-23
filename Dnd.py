from discord.ext.commands import Cog
from discord.ext import commands
import random
import json


class Dnd(Cog):
    def __init__(self, bot, stats, admins):
        self.bot = bot
        self.stats = stats
        self.admins = admins

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
            msg += f"\nAlive - {len(self.stats['characters']['alive'])}:\n"
            msg += "```\n"
            if self.stats["characters"]["alive"]:
                for character in self.stats["characters"]["alive"]:
                    msg += f"{character['name']} - {character['class']}\n"
            else:
                msg += "None\n"
            msg += "```"
        if status == "retired" or status == "all":
            msg += f"\nRetired - {len(self.stats['characters']['retired'])}:\n"
            msg += "```\n"
            if self.stats["characters"]["retired"]:
                for character in self.stats["characters"]["retired"]:
                    msg += f"{character['name']} - {character['class']}\n"
            else:
                msg += "None\n"
            msg += "```"
        if status == "dead" or status == "all":
            msg += f"\nDead - {len(self.stats['characters']['dead'])}:\n"
            msg += "```\n"
            if self.stats["characters"]["dead"]:
                for character in self.stats["characters"]["dead"]:
                    msg += f"{character['name']} - {character['class']}\n"
            else:
                msg += "None\n"
            msg += "```"
        await ctx.send(msg)

    @commands.group(name="character")
    async def character(self, ctx):
        """Shows detailed info for a given character name."""
        if ctx.invoked_subcommand is None:
            characters = self.stats["characters"]["alive"] + self.stats["characters"]["retired"] + \
                self.stats["characters"]["dead"]
            chosen = None
            for character in characters:
                if character["name"] == ctx.subcommand_passed:
                    chosen = character
            if not chosen:
                await ctx.send("No character found by that name. Use .characters to see a list of all characters.")
                return

            await ctx.send(f"```Name: {chosen['name']}:\nLevel: {chosen['level']}\nClass: {chosen['class']}```")

    @character.command(name="add")
    async def add_character(self, ctx, name, level, dclass):
        """Add a class to the list. Assumes the character starts alive."""
        character = {"name": name, "level": level, "class": dclass}
        self.stats["characters"]["alive"].append(character)
        with open('stats.json', 'w') as f:
            json.dump(self.stats, f)
        await ctx.send("Character has been added. Use .character <name> to see it.")

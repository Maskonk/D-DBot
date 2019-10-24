from discord.ext.commands import Cog
from discord.ext import commands
import random
import json
import sqlite3


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

        try:
            db = sqlite3.connect('dnd.db')
            conn = db.cursor()
            conn.execute("select characters.name, characters.level, characters.class, status.status "
                         "from characters join status on characters.status = status.id order by characters.status, "
                         "characters.name")
            characters = conn.fetchall()
            await ctx.send(characters)
        except Exception as e:
            print(e)
            await ctx.send("An error has occurred with this command, please make sure the status you are entering is "
                           "valid and  try again. If this error persists please report it to Punky.")
        finally:
            if db:
                db.close()

        alive = list(filter(lambda character: character[3] == "alive", characters))
        retired = list(filter(lambda character: character[3] == "retired", characters))
        dead = list(filter(lambda character: character[3] == "dead", characters))

        msg = "The current characters I have registered are:\n"
        if status == "alive" or status == "all":
            msg += f"\nAlive - {len(alive)}:\n"
            msg += "```\n"
            if alive:
                for character in alive:
                    msg += f"{character[0]} - {character[2]}\n"
            else:
                msg += "None\n"
            msg += "```"
        if status == "retired" or status == "all":
            msg += f"\nRetired - {len(retired)}:\n"
            msg += "```\n"
            if retired:
                for character in retired:
                    msg += f"{character[0]} - {character[2]}\n"
            else:
                msg += "None\n"
            msg += "```"
        if status == "dead" or status == "all":
            msg += f"\nDead - {len(dead)}:\n"
            msg += "```\n"
            if dead:
                for character in dead:
                    msg += f"{character[0]} - {character[2]}\n"
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

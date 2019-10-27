from discord.ext.commands import Cog
from discord.ext import commands
from random import randint
from util import db_call


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
                num = randint(1, 6)
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
        valid = ["alive", "retired", "dead", "all"]
        if status not in valid:
            await ctx.send("That is not a valid status, Please use alive, retired, dead or all.")
            return

        characters = await db_call(ctx, "select characters.name, characters.level, characters.class, status.status"
                                       " from characters join status on characters.status = status.id "
                                       "order by characters.status, characters.name")

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

            character = await db_call(ctx, "select characters.name, characters.level, characters.class, "
                                                "characters.owner, status.status from characters "
                                                "join status on status.id = characters.status where name=?",
                                                [ctx.subcommand_passed])
            if character:
                character = character[0]
                owner = self.bot.get_user(character[3])
                await ctx.send(f"```Name: {character[0]}:\nLevel: {character[1]}\nClass: {character[2]}"
                               f"\nStatus: {character[4].capitalize()}\nOwner: {owner.display_name}```")
            else:
                await ctx.send("No character found by that name. Use .characters to see a list of all characters.")

    @character.command(name="add")
    async def add_character(self, ctx, name, level, dclass):
        """Add a class to the list. Assumes the character starts alive."""
        character = [name, level, dclass, ctx.author.id, 1]
        await db_call(ctx, "insert into characters (name, level, class, owner, status) values (?,?,?,?,?)", character)
        await ctx.send("Character has been added. Use .character <name> to see it.")

    # async def db_call(self, ctx, sql, filtered=[]):
    #     try:
    #         db = connect('dnd.db')
    #         conn = db.cursor()
    #         conn.execute(sql, filtered)
    #         db.commit()
    #         return conn.fetchall()
    #     except Exception as e:
    #         print(e)
    #         await ctx.send("An error has occurred with this command, please try again. "
    #                        "If this error persists please report it to Punky.")
    #     finally:
    #         if db:
    #             db.close()

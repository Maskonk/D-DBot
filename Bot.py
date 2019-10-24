from discord.ext.commands import Bot
from discord import Game
from RightingWrongs import RightingWrongs
from Dnd import Dnd
from json import load

bot_prefix = "."
with open('token.txt', 'r') as f:
    token = f.read()

with open('stats.json', 'r') as f:
    stats = load(f)

client = Bot(command_prefix=bot_prefix)
admins = [167967067222441984, 168009927015661568]


@client.event
async def on_ready():
    await client.change_presence(activity=Game(name='D&D'))
    print("Online")


@client.event
async def on_command_error(ctx, error):
    print(error)
    if ctx.author.id == 247328517207883776:
        await ctx.message.delete()
        await ctx.author.send("No MadRat that is NOT a valid command.")
    else:
        await ctx.send("That is not a valid command. Please use *.help* for a list of all commands.")


@client.command(aliases=["Suggestions", "Suggest", "suggest", "suggestion", "Suggestion"])
async def suggestions(ctx):
    """Message pertaining to suggestions for the bot."""
    await ctx.send("If you have any suggestions for new features or an existing feature that could be made better feel "
                   "free to message Punky with your idea. (No promises it will be implemented though)")


@client.command()
async def git(ctx):
    """Alternate command for those trying to get the github link."""
    await ctx.send("git commit -m \"Did you mean .github command?\". (A git joke)")


@client.command(aliases=["code", "Code"])
async def github(ctx):
    """Link to the github repo for this bot."""
    await ctx.send("The code for this bot is at: https://github.com/Maskonk/DnDBot")


client.add_cog(Dnd(client, stats, admins))
client.add_cog(RightingWrongs(client, stats, admins))
client.run(token)

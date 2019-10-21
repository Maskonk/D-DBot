from discord.ext.commands import Bot
from RightingWrongs import RightingWrongs
from Dnd import Dnd

bot_prefix = "."
with open('token.txt', 'r') as f:
    token = f.read()
client = Bot(command_prefix=bot_prefix)


@client.event
async def on_ready():
    print("Online")


@client.command(aliases=["Suggestions", "Suggest", "suggest"])
async def suggestions(ctx):
    """Message pertaining to suggestions for the bot."""
    await ctx.send("If you have any suggestions for new features or an existing feature that could be made better feel "
                   "free to message Punky with your idea. (No promises it will be implemented though)")


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



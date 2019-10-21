from discord.ext.commands import Cog
from discord.ext import commands
from datetime import datetime
import calendar


class RightingWrongs(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.next_session = datetime(2019, 10, 31, 17, 30, 00)
        self.authorized = [167967067222441984, 168009927015661568]

    @commands.command(aliases=["wa", "WA", "WorldAnvil", "Worldanvil"])
    async def worldanvil(self, ctx):
        """Link to the campaign's World Anvil page."""
        await ctx.send("The link to the World Anvil page is:\nhttps://www.worldanvil.com/w/ehldaron-sebaddon")

    @commands.command()
    async def calender(self, ctx):
        """Link to the campaign's World Anvil page."""
        await ctx.send("The link to the calender page is:"
                       "\nhttps://fantasy-calendar.com/calendar.php?action=view&id=b74c2e0d1ff97f48c05b8270b043afd0")

    @commands.command(aliases=["nextsession", "Next", "next_session"])
    async def next(self, ctx):
        """The next session of the Righting Wrongs Campaign."""

        await ctx.send(f"The next session of Righting Wrongs will be on "
                       f"{calendar.day_name[self.next_session.weekday()]} "
                       f"the {self.next_session.day}{self.get_indicator(self.next_session.day)} of "
                       f"{calendar.month_name[self.next_session.month]}, "
                       f"starting at {self.next_session.hour}h{self.next_session.minute} UK time or "
                       f"{self.next_session.hour + 1}h{self.next_session.minute} Belgian time.")

    @commands.command(aliases=["Update", ])
    async def update(self, ctx, date, time="17:30"):
        """To update the next session of the Righting Wrongs Campaign's date. Restricted to Seb and Punky.
        Format dd/mm/yy hh:mm, hour in UK time."""
        if ctx.author.id not in self.authorized:
            await ctx.send("You are not authorized to update the session date.")
            return

        date = date.split("/")
        if int(date[2]) < 100:
            date[2] = int(date[2]) + 2000

        if ":" in time:
            time = time.split(":")
        elif "h" in time:
            time = time.split("h")

        self.next_session = datetime(int(date[2]), int(date[1]), int((date[0])), (int(time[0])), int(time[1]), 00)

        await ctx.send("Date updated.")
        command = self.bot.get_command("next")
        await ctx.invoke(command)

    def get_indicator(self, day):
        """Returns the indicator for the given number based on the last digit."""
        nth = {"1": "st", "2": "nd", "3": "rd"}
        if str(day)[-1] in nth.keys():
            return nth[str(day)[-1]]
        else:
            return "th"
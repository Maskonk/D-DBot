from discord.ext.commands import Cog
from discord.ext import commands
from datetime import datetime
from calendar import month_name, day_name
from re import split
from json import dump
from util import db_call


class RightingWrongs(Cog):
    def __init__(self, bot, stats, admins):
        self.bot = bot
        self.stats = stats
        next_date = split("\D+", stats["statistics"]["next"])
        self.next_session = datetime(int(next_date[0]), int(next_date[1]), int(next_date[2]), int(next_date[3]),
                                     int(next_date[4]), int(next_date[5]))
        self.authorized = admins

    @commands.command(name="neartpks", aliases=["tpks"])
    async def neartpks(self, ctx):
        """Shows the number of near Total Party Kills so far this campaign."""
        if ctx.invoked_subcommand is None:
            count = await db_call(ctx, "select count(*) from near_tpks")
            await ctx.send(f"The party has had {count[0][0]} near Total Party Kills so far this campaign.")

    @commands.group(name="near_tpk", aliases=["tpk"])
    async def near_tpk(self, ctx):
        """Lists the information for a given TPK."""
        if ctx.invoked_subcommand is None:
            info = await db_call(ctx, "select session_id, notes from near_tpks where id=?", [ctx.subcommand_passed])
            await ctx.send(f"```The near TPK happened in session number {info[0][0]}"
                           f"\nNotes from the near TPK: {info[0][1]}```")

    @near_tpk.command(name="add")
    async def add_tpk(self, ctx, session_no, notes=""):
        """Adds a near TPK to the database. Restricted to Seb and Punky."""
        if ctx.author.id not in self.authorized:
            await ctx.send("You are not authorized to add to the near TPK count.")
            return
        await db_call(ctx, "insert into near_tpks (session_id, notes) values (?, ?)", [session_no, notes])
        await ctx.send("Near Total Party Kills updated.")
        command = self.bot.get_command("neartpks")
        await ctx.invoke(command)

    @commands.command(name="sessions", aliases=["played"])
    async def sessions(self, ctx):
        """Shows the number of sessions played so far this campaign."""
        if ctx.invoked_subcommand is None:
            count = await db_call(ctx, "select count(*) from sessions")
            await ctx.send(f"The party has had {count[0][0]} sessions so far this campaign.")

    @commands.group(name="session", aliases=[])
    async def session(self, ctx):
        if ctx.invoked_subcommand is None:
            info = await db_call(ctx, "select date, notes from sessions where id=?", [ctx.subcommand_passed])
            await ctx.send(f"```Session number {ctx.subcommand_passed} happened on {info[0][0]}."
                           f"\nNotes from the session:\n{info[0][1]}```")

    @session.command(name="add")
    async def add_session(self, ctx, date=datetime.today().date(), notes=""):
        """Adds a session to the database. Restricted to Seb and Punky."""
        if ctx.author.id not in self.authorized:
            await ctx.send("You are not authorized to add to the session count.")
            return
        await db_call(ctx, "insert into sessions (date, notes) values (?, ?)", [date, notes])
        await ctx.send("Session count updated.")
        command = self.bot.get_command("sessions")
        await ctx.invoke(command)

    @commands.command(aliases=["wa", "WA", "WorldAnvil", "Worldanvil", "worldanvil"])
    async def world_anvil(self, ctx):
        """Link to the campaign's World Anvil page."""
        await ctx.send("The link to the World Anvil page is:\nhttps://www.worldanvil.com/w/ehldaron-sebaddon")

    @commands.command()
    async def calender(self, ctx):
        """Link to the campaign's World Anvil page."""
        await ctx.send("The link to the calender page is:"
                       "\nhttps://fantasy-calendar.com/calendar.php?action=view&id=b74c2e0d1ff97f48c05b8270b043afd0")

    @commands.group(name="next", aliases=["Next"])
    async def next(self, ctx):
        """The next session of the Righting Wrongs Campaign."""
        if ctx.invoked_subcommand is None:
            date_difference = self.next_session - datetime.now()
            days = divmod(date_difference.total_seconds(), 86400)
            hours = divmod(days[1], 3600)
            minutes = divmod(hours[1], 60)
            seconds = divmod(minutes[1], 1)
            await ctx.send(f"The next session of Righting Wrongs will be on "
                           f"{day_name[self.next_session.weekday()]} "
                           f"the {self.next_session.day}{self.get_indicator(self.next_session.day)} of "
                           f"{month_name[self.next_session.month]}, "
                           f"starting at {self.next_session.hour}h{self.next_session.minute} UK time or "
                           f"{self.next_session.hour + 1}h{self.next_session.minute} Belgian time. "
                           f"In {days[0]: .0f} days {hours[0]: .0f} hours {minutes[0]: .0f} minutes {seconds[0]: .0f} seconds.")

    @next.command(name='update')
    async def update_next_session(self, ctx, date, time="17:30"):
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

        self.stats['statistics']["next"] = str(self.next_session)

        with open('stats.json', 'w') as f:
            dump(self.stats, f)

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

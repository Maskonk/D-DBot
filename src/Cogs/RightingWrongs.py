from discord.ext.commands import Cog
from discord.ext import commands
from datetime import datetime
from calendar import month_name, day_name
from re import split
from json import dump
from src.util import db_call, is_authorized


class RightingWrongs(Cog):
    def __init__(self, bot, stats):
        self.bot = bot
        self.stats = stats
        next_date = split("\D+", stats["statistics"]["next"])
        self.next_session = datetime(int(next_date[0]), int(next_date[1]), int(next_date[2]), int(next_date[3]),
                                     int(next_date[4]), int(next_date[5]))

    @commands.command(name="near_tpks", aliases=["tpks", "neartpks"])
    async def near_tpks(self, ctx):
        """Shows the number of near Total Party Kills so far this campaign."""
        if ctx.invoked_subcommand is None:
            count = await db_call(ctx, "select count(*) from near_tpks")
            await ctx.send(f"The party has had {count[0][0]} near Total Party Kills so far this campaign.")

    @commands.group(name="near_tpk", aliases=["tpk", "neartpk"])
    async def near_tpk(self, ctx):
        """Lists the information for a given TPK."""
        if ctx.invoked_subcommand is None:
            info = await db_call(ctx, "select near_tpks.session_id, near_tpks.notes, sessions.date from near_tpks "
                                      "join sessions on near_tpks.session_id = sessions.id where near_tpks.id=?",
                                      [ctx.subcommand_passed])
            if info:
                day = self.format_date(info[0][2])
                await ctx.send(f"```The near TPK happened on {day_name[day.weekday()]} the "
                               f"{day.day}{self.get_indicator(day.day)} of {month_name[day.month]} {day.year} "
                               f"in session number {info[0][0]}.\nNotes from the near TPK:\n{info[0][1]}```")
            else:
                count = await db_call(ctx, "select count(*) from near_tpks")
                await ctx.send(f"No tpk with that number found, please try a number between 1 and {count[0][0]}")

    @near_tpk.command(name="add")
    @commands.check(is_authorized)
    async def add_tpk(self, ctx, session_no, notes=""):
        """Adds a near TPK to the database. Restricted to Seb and Punky."""
        await db_call(ctx, "insert into near_tpks (session_id, notes) values (?, ?)", [session_no, notes])
        await ctx.send("Near Total Party Kills updated.")
        command = self.bot.get_command("neartpks")
        await ctx.invoke(command)

    @near_tpk.command(name="update")
    @commands.check(is_authorized)
    async def update_tpk(self, ctx, tpk_no, notes):
        """Update the notes for a given near TPK."""
        await db_call(ctx, "update near_tpks set (notes) = (?) where id=?", [notes, tpk_no])
        await ctx.send("Notes for that near TPK have been updated.")

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
            if info:
                day = self.format_date(info[0][0])
                await ctx.send(f"```Session number {ctx.subcommand_passed} happened on {day_name[day.weekday()]} the "
                               f"{day.day}{self.get_indicator(day.day)} of {month_name[day.month]} {day.year}."
                               f"\nNotes from the session:\n{info[0][1]}```")
            else:
                count = await db_call(ctx, "select count(*) from sessions")
                await ctx.send(f"No session with that number found, please try a number between 1 and {count[0][0]}")

    @session.command(name="add")
    @commands.check(is_authorized)
    async def add_session(self, ctx, date=datetime.today().date(), notes=""):
        """Adds a session to the database. Restricted to Seb and Punky."""
        await db_call(ctx, "insert into sessions (date, notes) values (?, ?)", [date, notes])
        await ctx.send("Session count updated.")
        command = self.bot.get_command("sessions")
        await ctx.invoke(command)

    @session.command(name="update")
    @commands.check(is_authorized)
    async def update_session(self, ctx, session_no, notes):
        """Update the notes for a given session."""
        await db_call(ctx, "update sessions set (notes) = (?) where id=?", [notes, session_no])
        await ctx.send("Notes for that session have been updates.")

    @commands.command(aliases=["wa", "WA", "WorldAnvil", "Worldanvil", "worldanvil"])
    async def world_anvil(self, ctx):
        """Link to the campaign's World Anvil page."""
        await ctx.send("The link to the World Anvil page is:\nhttps://www.worldanvil.com/w/ehldaron-sebaddon")

    @commands.command()
    async def calender(self, ctx):
        """Link to the campaign's World Anvil page."""
        await ctx.send("The link to the calender page is:"
                       "\nhttps://fantasy-calendar.com/calendar.php?action=view&id=b74c2e0d1ff97f48c05b8270b043afd0")

    @commands.group(name="next_session", aliases=["next", "Next"])
    async def next_session(self, ctx):
        """The next session of the Righting Wrongs Campaign."""
        if ctx.invoked_subcommand is None:
            date_difference = self.next_session - datetime.now()
            days = divmod(date_difference.total_seconds(), 86400)
            hours = divmod(days[1], 3600)
            minutes = divmod(hours[1], 60)
            seconds = divmod(minutes[1], 1)
            msg = f"The next session of Righting Wrongs will be on {day_name[self.next_session.weekday()]} " \
                  f"the {self.next_session.day}{self.get_indicator(self.next_session.day)} of " \
                  f"{month_name[self.next_session.month]}, starting at {self.next_session.hour}h" \
                  f"{self.next_session.minute} UK time or {self.next_session.hour + 1}h{self.next_session.minute} " \
                  f"Belgian time."

            if self.next_session > datetime.now():
                msg += "\nIn "
                if days[0] > 0:
                    msg += f"{days[0]: .0f} days "
                if hours[0] > 0:
                    msg += f"{hours[0]: .0f} hours "
                if minutes[0] > 0:
                    msg += f"{minutes[0]: .0f} minutes "
                if seconds[0] > 0:
                    msg += f"{seconds[0]: .0f} seconds."

            else:
                msg += "\nThis date has already passed and a new one should be added soon."
            await ctx.send(msg)

    @next_session.command(name='update')
    @commands.check(is_authorized)
    async def update_next_session(self, ctx, date, time="17:30"):
        """To update the next session of the Righting Wrongs Campaign's date. Restricted to Seb and Punky.
                Format dd/mm/yy hh:mm, hour in UK time."""

        date = date.split("/")
        if int(date[2]) < 100:
            date[2] = int(date[2]) + 2000

        if ":" in time:
            time = time.split(":")
        elif "h" in time:
            time = time.split("h")

        new_date = datetime(int(date[2]), int(date[1]), int((date[0])), (int(time[0])), int(time[1]), 00)

        if new_date < datetime.now():
            await ctx.send("That date has already passed. Please enter a future date.")
            return

        self.next_session = new_date

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

    def format_date(self, date):
        date = date.split("-")
        day = datetime(int(date[0]), int(date[1]), int(date[2]), 17, 30, 00)
        return day

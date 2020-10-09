from discord.ext.commands import Cog, context
from discord.ext import commands
from datetime import datetime
from calendar import month_name, day_name
from src.util import db_call, is_authorized
from discord import Member
from dateutil.parser import parse


class Campaign(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="near_tpks", aliases=["tpks", "neartpks"])
    async def near_tpks(self, ctx: context) -> None:
        """Shows the number of near Total Party Kills so far this campaign."""
        if ctx.invoked_subcommand is None:
            count = await db_call(ctx, "select count(*) from near_tpks")
            await ctx.send(f"The party has had {count[0][0]} near Total Party Kills so far this campaign.")

    @commands.group(name="near_tpk", aliases=["tpk", "neartpk"], invoke_without_command=True)
    async def near_tpk(self, ctx: context) -> None:
        """Lists the information for a given TPK."""
        if ctx.invoked_subcommand is None:
            session_no = ctx.message.content.split()[-1]
            info = await db_call(ctx, "select near_tpks.session_id, near_tpks.notes, sessions.date from near_tpks "
                                      "join sessions on near_tpks.session_id = sessions.id where near_tpks.id=?",
                                      [session_no])
            if info:
                day = self.format_date(info[0][2], "00:00")
                await ctx.send(f"```The near TPK happened on {day_name[day.weekday()]} the "
                               f"{day.day}{self.get_indicator(day.day)} of {month_name[day.month]} {day.year} "
                               f"in session number {info[0][0]}.\nNotes from the near TPK:\n{info[0][1]}```")
            else:
                count = await db_call(ctx, "select count(*) from near_tpks")
                await ctx.send(f"No tpk with that number found, please try a number between 1 and {count[0][0]}")

    @near_tpk.command(name="add", invoke_without_command=True)
    @commands.check(is_authorized)
    async def add_tpk(self, ctx: context, session_no: int, *notes) -> None:
        """Adds a near TPK to the database. Restricted to Seb and Punky."""
        if not notes:
            notes = ""
        else:
            notes = " ".join(notes)

        await db_call(ctx, "insert into near_tpks (session_id, notes) values (?, ?)", [session_no, notes])
        await ctx.send("Near Total Party Kills updated.")
        command = self.bot.get_command("neartpks")
        await ctx.invoke(command)

    @near_tpk.command(name="update")
    @commands.check(is_authorized)
    async def update_tpk(self, ctx: context, tpk_no: int, *notes: int) -> None:
        """Update the notes for a given near TPK."""
        if not notes:
            notes = ""
        else:
            notes = " ".join(notes)

        await db_call(ctx, "update near_tpks set (notes) = (?) where id=?", [notes, tpk_no])
        await ctx.send("Notes for that near TPK have been updated.")

    @commands.command(name="sessions", aliases=["played"])
    async def sessions(self, ctx: context) -> None:
        """Shows the number of sessions played so far this campaign."""
        if ctx.invoked_subcommand is None:
            count = await db_call(ctx, "select count(*) from sessions")
            await ctx.send(f"The party has had {count[0][0]} sessions so far this campaign.")

    @commands.group(name="session", aliases=[], invoke_without_command=True)
    async def session(self, ctx: context) -> None:
        if ctx.invoked_subcommand is None:
            session_no = ctx.message.content.split()[-1]
            info = await db_call(ctx, "select date, notes from sessions where id=?", [session_no])
            if info:
                day = self.format_date(info[0][0])
                await ctx.send(f"```Session number {session_no} happened on {day_name[day.weekday()]} the "
                               f"{day.day}{self.get_indicator(day.day)} of {month_name[day.month]} {day.year}."
                               f"\nNotes from the session:\n{info[0][1]}```")
            else:
                count = await db_call(ctx, "select count(*) from sessions")
                await ctx.send(f"No session with that number found, please try a number between 1 and {count[0][0]}")

    @session.command(name="add")
    @commands.check(is_authorized)
    async def add_session(self, ctx: context, date: str = None, time: str = None, *notes: list) -> None:
        """Adds a session to the database. Restricted to Seb and Punky."""
        if date is None:
            date = datetime.today().date()
        else:
            date = self.format_date(date, time)

        if not notes:
            notes = ""
        else:
            notes = " ".join(notes)

        await db_call(ctx, "insert into sessions (date, notes) values (?, ?)", [date, notes])
        await ctx.send("Session count updated.")
        command = self.bot.get_command("sessions")
        await ctx.invoke(command)

    @session.command(name="update")
    @commands.check(is_authorized)
    async def update_session(self, ctx: context, session_no: int, *notes: list) -> None:
        """Update the notes for a given session."""

        if not notes:
            notes = ""
        else:
            notes = " ".join(notes)

        await db_call(ctx, "update sessions set (notes) = (?) where id=?", [notes, session_no])
        await ctx.send("Notes for that session have been updates.")

    @commands.group(name="next", aliases=[], invoke_without_command=True)
    async def next(self, ctx: context, campaign_abb: list) -> None:
        """The next session of the Righting Wrongs Campaign."""
        if ctx.invoked_subcommand is None:
            db = await db_call(ctx, "select date, name from next_sessions join campaigns on next_sessions.campaign = "
                                    "campaigns.id where campaigns.abbreviation=?", [campaign_abb])
            if not db:
                await ctx.send("That is not a valid campaign name, please make sure your capitalization is correct.")
                return

            campaign_name = db[0][1]
            date = datetime.strptime(f"{db[0][0]} 19:00:00", "%Y-%m-%d %H:%M:%S")
            date_difference = date - datetime.now()
            days = divmod(date_difference.total_seconds(), 86400)
            hours = divmod(days[1], 3600)
            minutes = divmod(hours[1], 60)
            seconds = divmod(minutes[1], 1)
            msg = f"The next session of {campaign_name} will be on {day_name[date.weekday()]} " \
                  f"the {date.day}{self.get_indicator(date.day)} of " \
                  f"{month_name[date.month]}, starting at {date.hour}h" \
                  f"{date.minute} UK time or {date.hour + 1}h{date.minute} " \
                  f"Belgian time."

            if date > datetime.now():
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

    @next.command(name='update', aliases=["update_next", "Update"])
    @commands.check(is_authorized)
    async def update_next_session(self, ctx: context, campaign: str, date: str, time: str = "19:00") -> None:
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

        l = await db_call(ctx, "select id, abbreviation from campaigns where abbreviation=?", [campaign])
        id, name = l[0]
        if not id:
            await ctx.send("That is not a valid campaign name, please make sure your capitalization is correct.")
            return

        await db_call(ctx, "update next_sessions set (date) = (?) where id=?", [new_date.date(), int(id)])

        await ctx.send("Date updated.")
        command = self.bot.get_command("next")
        await ctx.invoke(command, name)

    @commands.command()
    @commands.check(is_authorized)
    async def ping(self, ctx: context, abb: str) -> None:
        """Ping for the next session of thew Righting Wrongs campaign."""

        db = await db_call(ctx, "select date, name, role from next_sessions join campaigns on next_sessions.campaign = "
                                "campaigns.id where campaigns.abbreviation=?", [abb])
        if not db:
            await ctx.send("That is not a valid campaign name, please make sure your capitalization is correct.")
            return

        campaign_name = db[0][1]
        date = datetime.strptime(f"{db[0][0]} 19:00:00", "%Y-%m-%d %H:%M:%S")
        role_id = int(db[0][2])
        date_difference = date - datetime.now()
        role = ctx.guild.get_role(role_id)
        days = divmod(date_difference.total_seconds(), 86400)
        hours = divmod(days[1], 3600)
        minutes = divmod(hours[1], 60)
        seconds = divmod(minutes[1], 1)
        msg = f"{role.mention} The next session of {campaign_name} will be on {day_name[date.weekday()]} "\
              f"the {date.day}{self.get_indicator(date.day)} of " \
              f"{month_name[date.month]}, starting at {date.hour}h" \
              f"{date.minute} UK time or {date.hour + 1}h{date.minute} " \
              f"Belgian time."
        if date > datetime.now():
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

    @commands.command()
    @commands.check(is_authorized)
    async def late(self, ctx: context, abb: str, user: Member) -> None:
        """Telling people they're late!"""

        db = await db_call(ctx, "select date from next_sessions join campaigns on next_sessions.campaign = "
                                "campaigns.id where campaigns.abbreviation=?", [abb])
        if not db:
            await ctx.send("That is not a valid campaign name, please make sure your capitalization is correct.")
            return

        date = datetime.strptime(f"{db[0][0]} 19:00:00", "%Y-%m-%d %H:%M:%S")

        if date < datetime.now():
            date_difference = datetime.now() - date
            days = divmod(date_difference.total_seconds(), 86400)
            hours = divmod(days[1], 3600)
            minutes = divmod(hours[1], 60)
            seconds = divmod(minutes[1], 1)
            msg = f"{user.mention} you are late! The session was supposed to start at {date.hour}h" \
                  f"{date.minute} UK time or {date.hour + 1}h{date.minute} " \
                  f"Belgian time.\n"
            if days[0] > 0:
                msg += f"{days[0]: .0f} days "
            if hours[0] > 0:
                msg += f"{hours[0]: .0f} hours "
            if minutes[0] > 0:
                msg += f"{minutes[0]: .0f} minutes "
            if seconds[0] > 0:
                msg += f"{seconds[0]: .0f} seconds late."
        else:
            msg = f"{user.nick} is not late yet, hold your horses."

        await ctx.send(msg)

    @commands.command(aliases=["wa", "WA", "WorldAnvil", "Worldanvil", "worldanvil"])
    async def world_anvil(self, ctx: context) -> None:
        """Link to the campaign's World Anvil page."""
        await ctx.send("The link to the World Anvil page is:\nhttps://www.worldanvil.com/w/ehldaron-sebaddon")

    @commands.command()
    async def calender(self, ctx: context) -> None:
        """Link to the campaign's World Anvil page."""
        await ctx.send("The link to the calender page is:"
                       "\nhttps://fantasy-calendar.com/calendar.php?action=view&id=b74c2e0d1ff97f48c05b8270b043afd0")

    @staticmethod
    def get_indicator(day: int) -> str:
        """Returns the indicator for the given number based on the last digit."""
        nth = {"1": "st", "2": "nd", "3": "rd"}
        if str(day)[-1] in nth.keys():
            return nth[str(day)[-1]]
        else:
            return "th"

    def format_date(self, date: str, time: str = "") -> datetime.date:
        return parse(f"{date} {time}")

    def get_next_session(self, campaign_abb: str) -> str:
        pass

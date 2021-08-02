from discord.ext.commands import Cog, context
from discord.ext import commands
from datetime import datetime
from calendar import month_name, day_name
from src.util import db_call, is_authorized
from discord import Member
from dateutil.parser import parse
from arrow import now, get


class Campaign(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="near_tpks", aliases=["tpks", "neartpks"])
    async def near_tpks(self, ctx: context, campaign_abb: str) -> None:
        """Shows the number of near Total Party Kills so far this campaign."""
        campaign = await self.get_campaign(ctx, campaign_abb)
        if not campaign:
            return
        count = await db_call(ctx, "select count(*) from near_tpks where campaign_id = ?", [campaign["id"]])
        await ctx.send(f"The party has had {count[0][0]} near Total Party Kills so far this campaign.")

    @commands.group(name="near_tpk", aliases=["tpk", "neartpk"], invoke_without_command=True)
    async def near_tpk(self, ctx: context, campaign_abb: str, tpk_no: int) -> None:
        """Lists the information for a given TPK."""
        if ctx.invoked_subcommand is None:
            campaign = await self.get_campaign(ctx, campaign_abb)
            if not campaign:
                return
            info = await db_call(ctx, "select near_tpks.session_id, near_tpks.notes, sessions.date from near_tpks "
                                      "join sessions on near_tpks.session_id = sessions.id "
                                      "where near_tpks.campaign_id = ?",
                                      [campaign["id"]])

            if 1 <= tpk_no <= len(info):
                day = self.format_date(info[tpk_no-1][2])
                await ctx.send(f"```The near TPK happened on {day_name[day.weekday()]} the "
                               f"{day.day}{self.get_indicator(day.day)} of {month_name[day.month]} {day.year} "
                               f"in session number {info[tpk_no-1][0]}.\nNotes from the near TPK:\n"
                               f"{info[tpk_no-1][1]}```")
            else:
                count = await db_call(ctx, "select count(*) from near_tpks where campaign_id = ?", [campaign["id"]])
                await ctx.send(f"No tpk with that number found, please try a number between 1 and {count[0][0]}")

    @near_tpk.command(name="add", invoke_without_command=True)
    @commands.check(is_authorized)
    async def add_tpk(self, ctx: context, campaign_abb: str, session_no: int, *notes) -> None:
        """Adds a near TPK to the database. Restricted to Seb and Punky."""
        campaign = await self.get_campaign(ctx, campaign_abb)
        if not campaign:
            return

        if not notes:
            notes = ""
        else:
            notes = " ".join(notes)

        await db_call(ctx, "insert into near_tpks (session_id, campaign_id, notes) values (?, ?, ?)",
                      [session_no, campaign["id"],  notes])
        await ctx.send("Near Total Party Kills updated.")

    @near_tpk.command(name="update", invoke_without_command=True)
    @commands.check(is_authorized)
    async def update_tpk(self, ctx: context, campaign_abb: str, tpk_no: int, *notes) -> None:
        """Update the notes for a given near TPK."""

        campaign = await self.get_campaign(ctx, campaign_abb)
        if not campaign:
            return

        info = await db_call(ctx, "select id from near_tpks where near_tpks.campaign_id = ?",
                             [campaign["id"]])

        if 1 <= tpk_no <= len(info):
            id = info[tpk_no-1][0]
            if not notes:
                notes = ""
            else:
                notes = " ".join(notes)
        await db_call(ctx, "update near_tpks set (notes) = (?) where id=?", [notes, id])
        await ctx.send("Notes for that near TPK have been updated.")

    @commands.command(name="sessions", aliases=["played"])
    async def sessions(self, ctx: context, campaign_abb: str) -> None:
        """Shows the number of sessions played so far this campaign."""
        campaign = await self.get_campaign(ctx, campaign_abb)
        if not campaign:
            return
        count = await db_call(ctx, "select count(*) from sessions where campaign = ?", [campaign["id"]])
        await ctx.send(f"That campaign has had {count[0][0]} sessions so far this campaign.")

    @commands.group(name="session", aliases=[], invoke_without_command=True)
    async def session(self, ctx: context, campaign_abb: str, session_no: int) -> None:
        """Shows the notes for a spefic session."""
        if ctx.invoked_subcommand is None:
            campaign = await self.get_campaign(ctx, campaign_abb)
            if not campaign:
                return
            campaign = await self.get_campaign(ctx, campaign_abb)
            if not campaign:
                return

            sessions = await db_call(ctx, "select date, notes from sessions where campaign = :id order by date",
                                     [int(campaign.get("id"))])
            if sessions:
                session = sessions[session_no-1]
                day = self.format_date(session[0])
                await ctx.send(f"```Session number {session_no} happened on {day_name[day.weekday()]} the "
                               f"{day.day}{self.get_indicator(day.day)} of {month_name[day.month]} {day.year}."
                               f"\nNotes from the session:\n{session[1]}```")
            else:
                count = await db_call(ctx, "select count(*) from sessions")
                await ctx.send(f"No session with that number found, please try a number between 1 and {count[0][0]}")

    @session.command(name="add")
    @commands.check(is_authorized)
    async def add_session(self, ctx: context, campaign_abb: str, date: str = None, time: str = None, *notes) \
            -> None:
        """Adds a session to the database. Restricted to Seb and Punky."""
        if date is None:
            date = datetime.today().date()
        else:
            date = self.format_date(date, time)

        if not notes:
            notes = ""
        else:
            notes = " ".join(notes)

        campaign = await self.get_campaign(ctx, campaign_abb)

        if not campaign:
            return
        await db_call(ctx, "insert into sessions (date, notes, campaign) values (?, ?, ?)",
                      [date, notes, int(campaign.get("id"))])
        await ctx.send("Session added.")
        command = self.bot.get_command("sessions")
        await ctx.invoke(command, campaign_abb)

    @session.command(name="update")
    @commands.check(is_authorized)
    async def update_session(self, ctx: context, campaign_abb: str, session_no: int, *notes) -> None:
        """Update the notes for a given session."""

        if not notes:
            notes = ""
        else:
            notes = " ".join(notes)

        campaign = await self.get_campaign(ctx, campaign_abb)

        if not campaign:
            return

        sessions = await db_call(ctx, "select id, date, notes from sessions where campaign = :id order by date",
                                 [int(campaign.get("id"))])
        if sessions:
            session = sessions[session_no - 1]
            session_id = session[0]

        await db_call(ctx, "update sessions set (notes) = (?) where id=?", [notes, session_id])
        await ctx.send("Notes for that session have been updates.")

    @commands.group(name="next", aliases=[], invoke_without_command=True)
    async def next(self, ctx: context, campaign_abb: str) -> None:
        """Shows the time until the next session of the a Campaign."""
        if ctx.invoked_subcommand is None:
            db = await db_call(ctx, "select date, name from next_sessions join campaigns on next_sessions.campaign = "
                                    "campaigns.id where campaigns.abbreviation=?", [campaign_abb])
            if not db:
                await ctx.send("That is not a valid campaign name, please make sure your capitalization is correct.")
                return

            campaign_name = db[0][1]
            date = get(db[0][0]).to("GMT+1")
            msg = f"The next session of {campaign_name} will be on {day_name[date.weekday()]} " \
                  f"the {date.day}{self.get_indicator(date.day)} of " \
                  f"{month_name[date.month]}, starting at {date.hour}h" \
                  f"{date.minute} UK time or {date.hour + 1}h{date.minute} " \
                  f"Belgian time."

            if date > now():
                msg += f"\n{date.humanize(granularity=['day', 'hour', 'minute'])}"

            else:
                msg += "\nThis date has already passed and a new one should be added soon."
            await ctx.send(msg)

    @next.command(name='update', aliases=["update_next", "Update"])
    @commands.check(is_authorized)
    async def update_next_session(self, ctx: context, campaign: str, date: str, time: str = "19:00",
                                  timezone: str = "GMT+1") -> None:
        """To update the next session of the Righting Wrongs Campaign's date. Restricted to Seb and Punky.
                Format dd/mm/yy hh:mm, hour in UK time."""
        date = parse(f"{date} {time}", dayfirst=True)
        date = get(date, tzinfo=timezone).to("GMT+1")
        print(date)
        if date < now().to(timezone):
            await ctx.send("That date has already passed. Please enter a future date.")
            return

        l = await db_call(ctx, "select id, abbreviation from campaigns where abbreviation=?", [campaign])
        id, name = l[0]
        if not id:
            await ctx.send("That is not a valid campaign name, please make sure your capitalization is correct.")
            return

        await db_call(ctx, "update next_sessions set (date) = (?) where id=?", [str(date), int(id)])

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

        if not db[0][2]:
            await ctx.send("No role to ping for that campaign.")
            return

        campaign_name = db[0][1]
        date = get(parse(db[0][0], dayfirst=True), tzinfo="GMT+1")
        role_id = int(db[0][2])
        role = ctx.guild.get_role(role_id)
        if not role:
            await ctx.send("Could not find that role.")
            return

        msg = f"{role.mention} The next session of {campaign_name} will be on {day_name[date.weekday()]} "\
              f"the {date.day}{self.get_indicator(date.day)} of " \
              f"{month_name[date.month]}, starting at {date.hour}h" \
              f"{date.minute} UK time or {date.hour + 1}h{date.minute} " \
              f"Belgian time."
        if date > now():
            msg += f"\n{date.humanize(granularity=['day', 'hour', 'minute'])}"

        else:
            msg += "\nThis date has already passed and a new one should be added soon."
        await ctx.send(msg)

    @commands.command(aliases=["wa", "WA", "WorldAnvil", "Worldanvil", "worldanvil"])
    async def world_anvil(self, ctx: context, campaign_abb: str) -> None:
        """Link to the campaign's World Anvil page."""
        campaign = await self.get_campaign(ctx, campaign_abb)
        if not campaign:
            return
        if campaign.get("wa"):
            await ctx.send(f"The link to the World Anvil page is:\n{campaign['wa']}")
        else:
            await ctx.send("That campaign does not have a World Anvil page registered.")

    @commands.command()
    async def calender(self, ctx: context, campaign_abb: str) -> None:
        """Link to the campaign's Calender page."""
        campaign = await self.get_campaign(ctx, campaign_abb)
        if not campaign:
            return
        if campaign.get("calender"):
            await ctx.send(f"The link to the calender page is:\n{campaign['calender']}")
        else:
            await ctx.send("That campaign does not have a calender page registered.")

    @staticmethod
    def get_indicator(day: int) -> str:
        """Returns the indicator for the given number based on the last digit."""
        nth = {"1": "st", "2": "nd", "3": "rd"}
        if str(day)[-1] in nth.keys():
            return nth[str(day)[-1]]
        else:
            return "th"

    @staticmethod
    def format_date(date: str, time: str = "") -> datetime.date:
        return parse(f"{date} {time}")

    @staticmethod
    async def get_campaign(ctx: context, campaign_abb: str) -> dict:
        db = await db_call(ctx, "select * from campaigns where abbreviation=?", [campaign_abb])
        if db:
            db = db[0]
            campaign = {"id": db[0], "name": db[1], "abbreviation": db[2], "gm": db[3], "role": db[4], "wa": db[5],
                        "calender": db[7], "active": db[6]}
            return campaign
        else:
            await ctx.send("There is no campaign with that name.")

    @staticmethod
    async def get_next_session(ctx: context, campaign_id: str) -> datetime:
        db = await db_call(ctx, "select date from next_sessions where campaign = ?", [campaign_id])
        date = db[0][0]
        date = Campaign.format_date(date)
        return date

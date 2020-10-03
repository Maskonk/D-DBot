from sqlite3 import connect


async def db_call(ctx, sql: str, filtered: tuple = ()) -> None:
    """
    Connects to the database for the bot and executes the gives SQL query on that database.
    :param ctx: The context for the command that wanted to connect to the DB, used for user error reporting.
    :param sql: The sql query to execute
    :param filtered: Any data to be inserted.
    """
    db = None
    try:
        db = connect('db/dnd.db')
        conn = db.cursor()
        conn.execute(sql, filtered)
        db.commit()
        return conn.fetchall()
    except Exception as e:
        print(e)
        await ctx.send("An error has occurred with this command, please try again. "
                       "If this error persists please report it to Punky.")
    finally:
        if db:
            db.close()


async def is_authorized(ctx):
    admins = [167967067222441984, 168009927015661568]
    return ctx.author.id in admins


async def bot_channel(ctx):
    return ctx.channel.id == 702193202786205799

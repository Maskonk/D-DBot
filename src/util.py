from sqlite3 import connect


async def db_call(ctx, sql: str, filtered: tuple = ()) -> None:
    """
    Connects to the database for the bot and executes the gives SQL query on that database.
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


async def is_authorized(ctx) -> bool:
    """
    A check for the bot for privileged commands if the user is authorized to use the command.
    :return: Boolean if the users id is in the list of authorized users.
    """
    return ctx.author.id in [167967067222441984, 168009927015661568]


async def bot_channel(ctx) -> bool:
    """
    A check for the bot to check if the channel a command is called in is the right channel.
    :return: Boolean if the channel id where the command is called is the channel the command can be called in.
    """
    return ctx.channel.id == 702193202786205799

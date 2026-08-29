from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import ContextTypes

from routes import route

from utils import edit

from database import (
    cur,
    db
)

from input import (
    start_input,
    stop_input
)

from admin.session import set, value

# =========================================================
# USER SUPPORT
# =========================================================

@route("support_manager")
async def support_manager(update, context):

    query = update.callback_query

    cur.execute(
        "SELECT COUNT(*) FROM contacts WHERE type='support'"
    )
    support = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM contacts WHERE type='channel'"
    )
    channel = cur.fetchone()[0]

    text = f"""📞 SUPPORT MANAGER

━━━━━━━━━━━━━━

👥 Total Support : {support}

📢 Total Channel : {channel}

━━━━━━━━━━━━━━

Select an option below.
"""

    keyboard = InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "👤 Support List",
                callback_data="support_list"
            ),

            InlineKeyboardButton(
                "📢 Channel List",
                callback_data="channel_list"
            )

        ],

        [

            InlineKeyboardButton(
                "➕ Add Support",
                callback_data="add_support"
            ),

            InlineKeyboardButton(
                "➕ Add Channel",
                callback_data="add_channel"
            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="admin"
            )

        ]

    ])

    await edit(
        query,
        text,
        keyboard
     )

@route("support_list")
async def support_list(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT id, username
        FROM contacts
        WHERE type='support'
        ORDER BY id
    """)

    rows = cur.fetchall()

    text = """👤 SUPPORT LIST

━━━━━━━━━━━━━━

"""

    if not rows:

        text += "No support added."

    keyboard = []

    for row in rows:

        text += f"• {row['username']}\n"

        keyboard.append([

            InlineKeyboardButton(
                f"❌ {row['username']}",
                callback_data=f"del_support_{row['id']}"
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "➕ Add Support",
            callback_data="add_support"
        )

    ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="support_manager"
        ),

        InlineKeyboardButton(
            "🏠 Admin",
            callback_data="admin"
        )

    ])

    await edit(
        query,
        text,
        InlineKeyboardMarkup(keyboard)
    )

@route("add_support")
async def add_support(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    from input import start_input

    start_input(
        update.effective_user.id,
        "add_support"
    )

    set(
        update.effective_user.id,
        "support_query",
        query
    )

    await edit(

        query,

"""➕ ADD SUPPORT

━━━━━━━━━━━━━━

Send Support Details

Format:

Name | @Username

""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="support_list"
                ),

                InlineKeyboardButton(
                    "🏠 Admin",
                    callback_data="admin"
                )

            ]

        ])

    )

async def save_add_support(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    if "|" not in text:

        await update.message.reply_text(
            "❌ Format:\n\nName | @Username"
        )
        return

    name, username = map(str.strip, text.split("|", 1))

    # Normalize Username
    if username.startswith("https://t.me/"):
        username = username.replace("https://t.me/", "")

    elif username.startswith("http://t.me/"):
        username = username.replace("http://t.me/", "")

    elif username.startswith("t.me/"):
        username = username.replace("t.me/", "")

    elif username.startswith("@"):
        username = username[1:]

    cur.execute(
        """
        SELECT id
        FROM contacts
        WHERE type='support'
        AND username=?
        """,
        (username,)
    )

    if cur.fetchone():

        await update.message.reply_text(
            "⚠️ Support already exists."
        )

        stop_input(update.effective_user.id)

        return

    cur.execute(
        """
        INSERT INTO contacts(
            type,
            display_name,
            username,
            created_at
        )
        VALUES(
            'support',
            ?, ?, datetime('now','localtime')
        )
        """,
        (name, username)
    )

    db.commit()

    stop_input(update.effective_user.id)

    try:
        await update.message.delete()
    except:
        pass

    query = value(
        update.effective_user.id,
        "support_query"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="support"
            ),
            InlineKeyboardButton(
                "🏠 Admin",
                callback_data="admin"
            )
        ]
    ])

    if query:

        await edit(
            query,
            f"""✅ Support Added

👤 Name : {name}

🔗 Username : @{username}""",
            keyboard
        )

    else:

        await update.message.reply_text(
            f"""✅ Support Added

👤 Name : {name}

🔗 Username : @{username}""",
            reply_markup=keyboard
        )

@route("add_channel")
async def add_channel(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    from input import start_input

    start_input(
        update.effective_user.id,
        "add_channel"
    )

    from data import set

    set(
        update.effective_user.id,
        "channel_query",
        query
    )

    await edit(

        query,

"""➕ ADD CHANNEL

━━━━━━━━━━━━━━

Send Channel Username

""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="channel_list"
                ),

                InlineKeyboardButton(
                    "🏠 Admin",
                    callback_data="admin"
                )

            ]

        ])

    )

async def save_add_channel(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    if "|" not in text:

        await update.message.reply_text(
            "❌ Format:\n\nName | @Username"
        )
        return

    name, username = map(str.strip, text.split("|", 1))

    # Normalize Username / Link

    username = username.strip()

    if username.startswith("@"):
        username = username[1:]

    username = username.replace("https://t.me/", "")
    username = username.replace("http://t.me/", "")
    username = username.replace("t.me/", "")

    cur.execute(
        """
        SELECT id
        FROM contacts
        WHERE type='channel'
        AND username=?
        """,
        (username,)
    )

    if cur.fetchone():

        await update.message.reply_text(
            "⚠️ Channel already exists."
        )

        stop_input(update.effective_user.id)

        return

    cur.execute(
        """
        INSERT INTO contacts(
            type,
            display_name,
            username,
            created_at
        )
        VALUES(
            'channel',
            ?, ?, datetime('now','localtime')
        )
        """,
        (name, username)
    )

    db.commit()

    stop_input(update.effective_user.id)

    try:
        await update.message.delete()
    except:
        pass

    query = value(
        update.effective_user.id,
        "channel_query"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="support"
            ),
            InlineKeyboardButton(
                "🏠 Admin",
                callback_data="admin"
            )
        ]
    ])

    if query:

        await edit(
            query,
            f"""✅ Channel Added

📢 Name : {name}

🔗 Username : @{username}""",
            keyboard
        )

    else:

        await update.message.reply_text(
            f"""✅ Channel Added

📢 Name : {name}

🔗 Username : @{username}""",
            reply_markup=keyboard
        )

@route("channel_list")
async def channel_list(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT
            id,
            username
        FROM contacts
        WHERE type='channel'
        ORDER BY id
    """)

    rows = cur.fetchall()

    text = "📢 CHANNEL LIST\n\n━━━━━━━━━━━━━━\n\n"

    if not rows:

        text += "No channel added."

    else:

        for row in rows:

            text += f"• {row['username']}\n"

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(
                f"❌ {row['username']}",
                callback_data=f"del_channel_{row['id']}"
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "➕ Add Channel",
            callback_data="add_channel"
        )

    ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="support_manager"
        ),

        InlineKeyboardButton(
            "🏠 Admin",
            callback_data="admin"
        )

    ])

    await edit(
        query,
        text,
        InlineKeyboardMarkup(keyboard)
    )

async def delete_channel(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cid = int(
        query.data.replace(
            "del_channel_",
            ""
        )
    )

    cur.execute(
        "DELETE FROM contacts WHERE id=?",
        (cid,)
    )

    db.commit()

    await query.answer(
        "✅ Channel Deleted."
    )

    await channel_list(update, context)


async def delete_support(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    sid = int(
        query.data.replace(
            "del_support_",
            ""
        )
    )

    cur.execute(
        "DELETE FROM contacts WHERE id=?",
        (sid,)
    )

    db.commit()

    await query.answer(
        "✅ Support Deleted."
    )

    await support_list(update, context)

@route("support")
async def support(update: Update,
                  context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT username
        FROM contacts
        WHERE type='support'
        ORDER BY id
    """)
    supports = cur.fetchall()

    cur.execute("""
        SELECT username
        FROM contacts
        WHERE type='channel'
        ORDER BY id
    """)
    channels = cur.fetchall()

    text = """📞 SUPPORT CENTER

━━━━━━━━━━━━━━

👤 Support Team

"""

    if supports:

        for row in supports:
            text += f"• {row['username']}\n"

    else:
        text += "No Support Available.\n"

    text += "\n━━━━━━━━━━━━━━\n\n📢 Official Channels\n\n"

    if channels:

        for row in channels:
            text += f"• {row['username']}\n"

    else:
        text += "No Channel Available."

    keyboard = []

    for row in supports:

        keyboard.append([
            InlineKeyboardButton(
                f"👤 {row['username']}",
                url=f"https://t.me/{row['username'].replace('@','')}"
            )
        ])

    for row in channels:

        keyboard.append([
            InlineKeyboardButton(
                f"📢 {row['username']}",
                url=f"https://t.me/{row['username'].replace('@','')}"
            )
        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="home"
        )

    ])

    await edit(
        query,
        text,
        InlineKeyboardMarkup(keyboard)
    )

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import ContextTypes

from routes import route
from input import (
    start_input,
    stop_input
)

from admin.session import (
    set,
    value
)

from utils import edit

from database import (
    db,
    cur
)

from input import (
    start_input,
    stop_input
)

from payments.session import (
    set,
    value,
    message
)

@route("users")
async def users(update: Update,
                context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute(
        "SELECT COUNT(*) FROM users"
    )
    total = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM users WHERE banned=0"
    )
    active = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM users WHERE banned=1"
    )
    banned = cur.fetchone()[0]

    await edit(

        query,

f"""👤 USER MANAGER

━━━━━━━━━━━━━━

👥 Total Users : {total}

🟢 Active Users : {active}

🔴 Banned Users : {banned}

━━━━━━━━━━━━━━

Select an option.
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🔍 Search User",
                    callback_data="search_user"
                )

            ],

            [

                InlineKeyboardButton(
                    "👥 All Users",
                    callback_data="all_users"
                )

            ],

            [

                InlineKeyboardButton(
                    "💰 Add Balance",
                    callback_data="admin_add_balance"
                ),

                InlineKeyboardButton(
                    "📜 History",
                    callback_data="user_history"
                )

            ],

            [

                InlineKeyboardButton(
                    "🚫 Ban User",
                    callback_data="ban_user"
                ),

                InlineKeyboardButton(
                    "✅ Unban User",
                    callback_data="unban_user"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="admin"
                )

            ]

        ])

    )


@route("all_users")
async def all_users(update: Update,
                    context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    admin_id = update.effective_user.id

    page = value(
        admin_id,
        "user_page"
    ) or 0

    limit = 20

    offset = page * limit

    cur.execute(
        "SELECT COUNT(*) FROM users"
    )

    total = cur.fetchone()[0]

    cur.execute(
        """
        SELECT *
        FROM users
        ORDER BY id DESC
        LIMIT ?
        OFFSET ?
        """,
        (
            limit,
            offset
        )
    )

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        status = "🔴" if row["banned"] else "🟢"

        keyboard.append([

            InlineKeyboardButton(

                f"{status} {row['first_name']} ({row['id']})",

                callback_data=f"user_{row['id']}"

            )

        ])

    nav = []

    if page > 0:

        nav.append(

            InlineKeyboardButton(
                "⬅️ Previous",
                callback_data="users_prev"
            )

        )

    if offset + limit < total:

        nav.append(

            InlineKeyboardButton(
                "➡️ Next",
                callback_data="users_next"
            )

        )

    if nav:

        keyboard.append(nav)

    keyboard.append([

        InlineKeyboardButton(
            "🔍 Search",
            callback_data="search_user"
        )

    ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="users"
        ),

        InlineKeyboardButton(
            "🏠 Admin",
            callback_data="admin"
        )

    ])

    await edit(

        query,

f"""👥 ALL USERS

━━━━━━━━━━━━━━

👤 Total Users : {total}

📄 Page : {page+1}

━━━━━━━━━━━━━━

Select a user.
""",

        InlineKeyboardMarkup(
            keyboard
        )

    )

@route("user_")
async def user_info(update: Update,
                    context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    uid = int(
        query.data.replace(
            "user_",
            ""
        )
    )

    set(
        update.effective_user.id,
        "selected_user",
        uid
    )

    cur.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (uid,)
    )

    row = cur.fetchone()

    if not row:

        await query.answer(
            "❌ User Not Found",
            show_alert=True
        )

        return

    status = (
        "🔴 Banned"
        if row["banned"]
        else "🟢 Active"
    )

    await edit(

        query,

f"""👤 USER PROFILE

━━━━━━━━━━━━━━

🆔 ID
➜ {row['id']}

👤 Name
➜ {row['first_name']}

📛 Username
➜ @{row['username'] or 'None'}

💰 Balance
➜ {row['balance']} Tk

🚫 Status
➜ {status}
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "💰 Add Balance",
                    callback_data="admin_add_balance"
                )

            ],

            [

                InlineKeyboardButton(
                    "🚫 Ban",
                    callback_data="ban_user"
                ),

                InlineKeyboardButton(
                    "✅ Unban",
                    callback_data="unban_user"
                )

            ],

            [

                InlineKeyboardButton(
                    "📜 History",
                    callback_data="user_history"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="all_users"
                ),

                InlineKeyboardButton(
                    "🏠 Admin",
                    callback_data="admin"
                )

            ]

        ])

    )


@route("users_prev")
async def users_prev(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    page = value(
        uid,
        "user_page"
    ) or 0

    if page > 0:

        set(
            uid,
            "user_page",
            page - 1
        )

    await all_users(
        update,
        context
    )


@route("users_next")
async def users_next(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    page = value(
        uid,
        "user_page"
    ) or 0

    set(
        uid,
        "user_page",
        page + 1
    )

    await all_users(
        update,
        context
    )

@route("ban_user")
async def ban_user(update: Update,
                   context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    admin_id = update.effective_user.id

    if admin_id != 8153757163:

        await query.answer(
            "⛔ Only the Owner can manage bans.",
            show_alert=True
        )
        return

    uid = value(
        admin_id,
        "selected_user"
    )

    if not uid:

        await query.answer(
            "❌ No user selected.",
            show_alert=True
        )

        return

    if uid == 8153757163:

        await query.answer(
            "❌ Owner cannot be banned.",
            show_alert=True
        )

        return

    cur.execute(
        """
        UPDATE users
        SET banned=1
        WHERE id=?
        """,
        (uid,)
    )

    db.commit()

    await query.answer(
        "✅ User Banned"
    )

    await user_info_by_id(
        update,
        context,
        uid
    )


@route("unban_user")
async def unban_user(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    admin_id = update.effective_user.id

    if admin_id != 8153757163:

        await query.answer(
            "⛔ Only the Owner can manage bans.",
            show_alert=True
        )
        return

    uid = value(
        admin_id,
        "selected_user"
    )

    if not uid:

        await query.answer(
            "❌ No user selected.",
            show_alert=True
        )
        return

        return

    cur.execute(
        """
        UPDATE users
        SET banned=0
        WHERE id=?
        """,
        (uid,)
    )

    db.commit()

    await query.answer(
        "✅ User Unbanned"
    )

    await user_info_by_id(
        update,
        context,
        uid
    )


async def user_info_by_id(update: Update,
                          context: ContextTypes.DEFAULT_TYPE,
                          uid: int):

    cur.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (uid,)
    )

    row = cur.fetchone()

    if not row:
        return

    status = (
        "🔴 Banned"
        if row["banned"]
        else "🟢 Active"
    )

    query = update.callback_query

    text = f"""👤 USER PROFILE

    ━━━━━━━━━━━━━━

    🆔 ID
    ➜ {row['id']}

    👤 Name
    ➜ {row['first_name']}

    📛 Username
    ➜ @{row['username'] or 'None'}

    💰 Balance
    ➜ {row['balance']} Tk

    🚫 Status
    ➜ {status}
    """

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "💰 Add Balance",
                callback_data="admin_add_balance"
            )
        ],

        [
            InlineKeyboardButton(
                "🚫 Ban",
                callback_data="ban_user"
            ),
            InlineKeyboardButton(
                "✅ Unban",
                callback_data="unban_user"
            )
        ],

        [
            InlineKeyboardButton(
                "📜 History",
                callback_data="user_history"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="all_users"
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
            text,
            keyboard
        )

    else:

        try:
            await update.message.delete()
        except:
            pass

        await update.message.reply_text(
            text,
            reply_markup=keyboard
        )


@route("user_history")
async def user_history(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    admin_id = update.effective_user.id

    uid = value(
        admin_id,
        "selected_user"
    )

    if not uid:

        await query.answer(
            "❌ No user selected.",
            show_alert=True
        )

        return

    cur.execute(
        """
        SELECT
            product,
            amount,
            purchase_date
        FROM orders
        WHERE user=?
        ORDER BY id DESC
        LIMIT 20
        """,
        (uid,)
    )

    rows = cur.fetchall()

    text = f"""📜 USER HISTORY

━━━━━━━━━━━━━━

👤 User ID : {uid}

━━━━━━━━━━━━━━

"""

    if not rows:

        text += "No purchase history found."

    else:

        for row in rows:

            text += (
                f"🛒 {row['product']}\n"
                f"💰 {row['amount']} Tk\n"
                f"🕒 {row['purchase_date']}\n\n"
            )

    await edit(

        query,

        text,

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data=f"user_{uid}"
                )

            ]

        ])

    )


@route("search_user")
async def search_user(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    start_input(
        update.effective_user.id,
        "search_user"
    )

    await edit(

        query,

"""🔍 SEARCH USER

━━━━━━━━━━━━━━

Send Telegram User ID
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="users"
                )

            ]

        ])

    )


async def save_search_user(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):

    admin_id = update.effective_user.id

    try:

        uid = int(
            update.message.text.strip()
        )

    except:

        await update.message.reply_text(
            "❌ Invalid User ID"
        )

        return

    stop_input(admin_id)

    await save_search_user_by_id(
        update,
        context,
        uid
    )


async def save_search_user_by_id(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE,
                                 uid: int):

    print("SEARCH USER CALLED")
    print(update.message.text)

    cur.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (uid,)
    )

    row = cur.fetchone()

    if not row:

        await update.message.reply_text(
            "❌ User Not Found"
        )

        return

    set(
        update.effective_user.id,
        "selected_user",
        uid
    )

    await user_info_by_id(
        update,
        context,
        uid
    )


@route("admin_add_balance")
async def admin_add_balance(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    start_input(
        update.effective_user.id,
        "admin_balance"
    )

    set(
        update.effective_user.id,
        "balance_msg",
        query.message.message_id
    )

    await edit(

        query,

"""💰 ADD USER BALANCE

━━━━━━━━━━━━━━

Send:

UserID Amount
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="users"
                )

            ]

        ])

    )


async def save_admin_balance(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):

    try:

        uid, amount = update.message.text.split()

        uid = int(uid)

        amount = int(amount)

    except:

        await update.message.reply_text(
          """❌ Format
━━━━━━━━━━━━━━
UserID Amount
"""
        )

        return

    cur.execute(
        """
        UPDATE users
        SET balance=balance+?
        WHERE id=?
        """,
        (
            amount,
            uid
        )
    )

    db.commit()

    stop_input(
        update.effective_user.id
    )

    try:

        await context.bot.send_message(

            uid,

f"""💰 Balance Added

━━━━━━━━━━━━━━

Amount :

{amount} Tk
"""

        )

    except:

        pass

    try:
        await update.message.delete()
    except:
        pass


    admin_id = update.effective_user.id

    msg_id = value(
        admin_id,
        "balance_msg"
    )

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=msg_id,
        text=f"""✅ BALANCE ADDED

    ━━━━━━━━━━━━━━

    👤 User ID :
    {uid}

    💰 Amount :
    {amount}

    ━━━━━━━━━━━━━━

    Balance Added Successfully.
    """,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="admin"
                )
            ]
        ])
    )



    stop_input(update.effective_user.id)

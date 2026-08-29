from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import ContextTypes

from routes import route

from database import (
    db,
    cur
)

from utils import edit

from input import (
    start_input,
    stop_input
)

from admin.session import (
    set,
    value
)

import random
import string

from datetime import (
    datetime,
    timedelta
)

from telegram import CopyTextButton

def redeem_code():

    while True:

        code = "RD-" + "".join(

            random.choices(

                string.ascii_uppercase +
                string.digits,

                k=8

            )

        )

        cur.execute(

            "SELECT id FROM redeem WHERE code=?",

            (code,)

        )

        if not cur.fetchone():

            return code

def redeem_back():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(

                "⬅️ Back",

                callback_data="admin_redeem_panel"

            ),

            InlineKeyboardButton(

                "🏠 Admin",

                callback_data="admin"

            )

        ]

    ])

def redeem_cancel():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(

                "❌ Cancel",

                callback_data="admin_redeem_panel"

            )

        ],

        [

            InlineKeyboardButton(

                "🏠 Admin",

                callback_data="admin"

            )

        ]

    ])


def info_back(rid):

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(

                "⬅️ Back",

                callback_data=f"admin_redeem_info_{rid}"

            ),

            InlineKeyboardButton(

                "🏠 Admin",

                callback_data="admin"

            )

        ]

    ])

def search_back():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(

                "⬅️ Back",

                callback_data="admin_redeem_list"

            ),

            InlineKeyboardButton(

                "🏠 Admin",

                callback_data="admin"

            )

        ]

    ])

# ==========================
# REDEEM PANEL
# ==========================

@route("admin_redeem_panel")
async def admin_redeem_panel(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute(
        "SELECT COUNT(*) FROM redeem"
    )
    total = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM redeem WHERE status=1"
    )
    active = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM redeem WHERE status=0"
    )
    disabled = cur.fetchone()[0]

    await edit(

        query,

f"""🎁 REDEEM MANAGEMENT

━━━━━━━━━━━━━━

📦 Total Redeem :
{total}

🟢 Active :
{active}

🔴 Disabled :
{disabled}

━━━━━━━━━━━━━━

Select an option.
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "➕ Create",
                    callback_data="admin_create_redeem"
                )

            ],

            [

                InlineKeyboardButton(
                    "📋 Redeem List",
                    callback_data="admin_redeem_list"
                )

            ],

            [

                InlineKeyboardButton(
                    "🔍 Search",
                    callback_data="admin_search_redeem"
                ),

                InlineKeyboardButton(
                    "📊 Stats",
                    callback_data="admin_redeem_stats"
                )

            ],

            [

                InlineKeyboardButton(
                    "📜 History",
                    callback_data="admin_redeem_history"
                )

            ],

            [

                InlineKeyboardButton(
                    "🏠 Admin Panel",
                    callback_data="admin"
                )

            ]

        ])

    )


# ==========================
# CREATE REDEEM
# ==========================

@route("admin_create_redeem")
async def admin_create_redeem(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    uid = update.effective_user.id

    start_input(
        uid,
        "admin_redeem_amount"
    )

    set(
        uid,
        "admin_redeem_msg",
        query.message.message_id
    )

    await edit(

        query,

"""➕ CREATE REDEEM

━━━━━━━━━━━━━━

💰 Step 1 / 4

Send Redeem Amount

Example

100
""",

        redeem_cancel()

    )

async def save_admin_redeem_amount(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    try:

        amount = int(update.message.text)

        if amount <= 0:
            raise ValueError

    except:

        await update.message.reply_text(
            "❌ Invalid Amount."
        )

        return

    set(uid, "redeem_amount", amount)

    start_input(uid, "admin_redeem_limit")

    try:
        await update.message.delete()
    except:
        pass

    msg = value(uid, "admin_redeem_msg")

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=msg,

        text="""➕ CREATE REDEEM

━━━━━━━━━━━━━━

👥 Step 2 / 4

Send Total Limit

Example

100
""",

        reply_markup=redeem_cancel()

    )

async def save_admin_redeem_limit(update: Update,
                                  context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    try:

        limit_count = int(update.message.text)

        if limit_count <= 0:
            raise ValueError

    except:

        await update.message.reply_text(
            "❌ Invalid Limit."
        )

        return

    set(uid, "redeem_limit", limit_count)

    start_input(uid, "admin_redeem_per_user")

    try:
        await update.message.delete()
    except:
        pass

    msg = value(uid, "admin_redeem_msg")

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=msg,

        text="""➕ CREATE REDEEM

━━━━━━━━━━━━━━

👤 Step 3 / 4

Send Per User Limit

Example

1

0 = Unlimited
""",

        reply_markup=redeem_cancel()

    )

async def save_admin_redeem_per_user(update: Update,
                                     context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    try:

        per_user = int(update.message.text)

        if per_user < 0:
            raise ValueError

    except:

        await update.message.reply_text(
            "❌ Invalid Value."
        )

        return

    set(uid, "redeem_per_user", per_user)

    start_input(uid, "admin_redeem_expiry")

    try:
        await update.message.delete()
    except:
        pass

    msg = value(uid, "admin_redeem_msg")

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=msg,

        text="""➕ CREATE REDEEM

━━━━━━━━━━━━━━

📅 Step 4 / 4

Send Expiry

Example

31-12-2026 23:59

Or

none
""",

        reply_markup=redeem_cancel()

    )

async def save_admin_redeem_expiry(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    expiry = update.message.text.strip()

    if expiry.lower() == "none":

        expiry = None

    else:

        try:

            datetime.strptime(
                expiry,
                "%d-%m-%Y %H:%M"
            )

        except:

            await update.message.reply_text(
                "❌ Invalid Date."
            )

            return

    code = redeem_code()

    cur.execute(

        """
        INSERT INTO redeem(

            code,
            amount,
            limit_count,
            used_count,
            per_user,
            expire_at,
            status

        )

        VALUES(?,?,?,?,?,?,?)

        """,

        (

            code,

            value(uid, "redeem_amount"),

            value(uid, "redeem_limit"),

            0,

            value(uid, "redeem_per_user"),

            expiry,

            1

        )

    )

    db.commit()

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    msg = value(uid, "admin_redeem_msg")

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=msg,

        text=f"""✅ REDEEM CREATED

━━━━━━━━━━━━━━

🔑 Code

`{code}`

━━━━━━━━━━━━━━

Successfully Created.
""",

        parse_mode="Markdown",

        reply_markup=InlineKeyboardMarkup([

            [

                InlineKeyboardButton(

                    "📋 Redeem List",

                    callback_data="admin_redeem_list"

                )

            ],

            [

                InlineKeyboardButton(

                    "➕ Create Again",

                    callback_data="admin_create_redeem"

                )

            ],

            [

                InlineKeyboardButton(

                    "🏠 Admin",

                    callback_data="admin"

                )

            ]

        ])

    )

@route("admin_search_redeem")
async def admin_search_redeem(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    uid = update.effective_user.id

    start_input(
        uid,
        "admin_search_redeem"
    )

    set(
        uid,
        "admin_redeem_msg",
        query.message.message_id
    )

    await edit(

        query,

"""🔍 SEARCH REDEEM

━━━━━━━━━━━━━━

Send Redeem Code

Example

RD-ABC12345
""",

        search_back()

    )


async def save_admin_search_redeem(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    code = update.message.text.strip()

    cur.execute(

        """
        SELECT *
        FROM redeem
        WHERE code=?
        """,

        (code,)

    )

    row = cur.fetchone()

    try:
        await update.message.delete()
    except:
        pass

    msg = value(
        uid,
        "admin_redeem_msg"
    )

    if not row:

        await context.bot.edit_message_text(

            chat_id=update.effective_chat.id,

            message_id=msg,

            text="""❌ REDEEM NOT FOUND""",

            reply_markup=search_back()

        )

        stop_input(uid)

        return

    stop_input(uid)

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=msg,

        text=f"""🔑 REDEEM FOUND

━━━━━━━━━━━━━━

Code :
{row['code']}

Amount :
{row['amount']} Tk
""",

        reply_markup=InlineKeyboardMarkup([

            [

                InlineKeyboardButton(

                    "📄 Details",

                    callback_data=f"admin_redeem_info_{row['id']}"

                )

            ],

            [

                InlineKeyboardButton(

                    "⬅️ Back",

                    callback_data="admin_redeem_list"

                ),

                InlineKeyboardButton(

                    "🏠 Admin",

                    callback_data="admin"

                )

            ]

        ])

    )

@route("admin_redeem_stats")
async def admin_redeem_stats(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute(
        "SELECT COUNT(*) FROM redeem"
    )
    total = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM redeem WHERE status=1"
    )
    active = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM redeem WHERE status=0"
    )
    disabled = cur.fetchone()[0]

    cur.execute(
        "SELECT SUM(used_count) FROM redeem"
    )
    used = cur.fetchone()[0] or 0

    await edit(

        query,

f"""📊 REDEEM STATISTICS

━━━━━━━━━━━━━━

📦 Total :
{total}

🟢 Active :
{active}

🔴 Disabled :
{disabled}

🎯 Total Used :
{used}
""",

        redeem_back()

    )

@route("admin_redeem_history")
async def admin_redeem_history(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute(

        """
        SELECT
            code,
            user_id,
            amount,
            used_at
        FROM redeem_history
        ORDER BY id DESC
        LIMIT 20
        """

    )

    rows = cur.fetchall()

    if not rows:

        await edit(

            query,

            "📭 No Redeem History.",

            redeem_back()

        )

        return

    text = "📜 REDEEM HISTORY\n\n"

    for row in rows:

        text += (
            f"🔑 {row['code']}\n"
            f"👤 {row['user_id']}\n"
            f"💰 {row['amount']} Tk\n"
            f"🕒 {row['used_at']}\n\n"
        )

    await edit(

        query,

        text,

        redeem_back()

    )

@route("admin_edit_redeem_amount")
async def admin_edit_redeem_amount(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    rid = int(
        query.data.replace(
            "admin_edit_redeem_amount_",
            ""
        )
    )

    uid = update.effective_user.id

    set(uid, "edit_redeem_id", rid)

    set(
        uid,
        "admin_redeem_msg",
        query.message.message_id
    )

    start_input(
        uid,
        "admin_edit_redeem_amount"
    )

    await edit(

        query,

"""💰 EDIT AMOUNT

━━━━━━━━━━━━━━

Send New Amount
""",

        info_back(rid)

    )

async def save_admin_edit_redeem_amount(update: Update,
                                        context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    rid = value(uid, "edit_redeem_id")

    try:

        amount = int(update.message.text)

        if amount <= 0:
            raise ValueError

    except:

        await update.message.reply_text(
            "❌ Invalid Amount."
        )

        return

    cur.execute(

        """
        UPDATE redeem
        SET amount=?
        WHERE id=?
        """,

        (
            amount,
            rid
        )

    )

    db.commit()

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    query = update.callback_query
    query.data = f"admin_redeem_info_{rid}"

    await admin_redeem_info(
        update,
        context
    )


@route("admin_edit_redeem_limit")
async def admin_edit_redeem_limit(update: Update,
                                  context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    rid = int(
        query.data.replace(
            "admin_edit_redeem_limit_",
            ""
        )
    )

    uid = update.effective_user.id

    set(uid, "edit_redeem_id", rid)

    set(
        uid,
        "admin_redeem_msg",
        query.message.message_id
    )

    start_input(
        uid,
        "admin_edit_redeem_limit"
    )

    await edit(

        query,

"""👥 EDIT LIMIT

━━━━━━━━━━━━━━

Send New Limit
""",

        info_back(rid)

    )

async def save_admin_edit_redeem_limit(update: Update,
                                       context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    rid = value(uid, "edit_redeem_id")

    try:

        limit_count = int(update.message.text)

        if limit_count <= 0:
            raise ValueError

    except:

        await update.message.reply_text(
            "❌ Invalid Limit."
        )

        return

    cur.execute(

        """
        UPDATE redeem
        SET limit_count=?
        WHERE id=?
        """,

        (
            limit_count,
            rid
        )

    )

    db.commit()

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    query = update.callback_query
    query.data = f"admin_redeem_info_{rid}"

    await admin_redeem_info(
        update,
        context
    )


# ==========================
# REDEEM DETAILS
# ==========================

@route("admin_redeem_info")
async def admin_redeem_info(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    rid = int(
        query.data.replace(
            "admin_redeem_info_",
            ""
        )
    )

    cur.execute(
        """
        SELECT *
        FROM redeem
        WHERE id=?
        """,
        (rid,)
    )

    row = cur.fetchone()

    if not row:

        await query.answer(
            "❌ Redeem Not Found",
            show_alert=True
        )

        return

    remaining = (
        row["limit_count"] -
        row["used_count"]
    )

    if remaining < 0:

        remaining = 0

    status = (
        "🟢 Active"
        if row["status"] == 1
        else "🔴 Disabled"
    )

    expiry = (
        row["expire_at"]
        if row["expire_at"]
        else "Unlimited"
    )

    await edit(

        query,

f"""🎁 REDEEM DETAILS

━━━━━━━━━━━━━━

🔑 Code
{row["code"]}

💰 Amount
{row["amount"]} Tk

👥 Total Limit
{row["limit_count"]}

✅ Used
{row["used_count"]}

📦 Remaining
{remaining}

👤 Per User
{row["per_user"]}

📅 Expiry
{expiry}

📊 Status
{status}
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "💰 Amount",
                    callback_data=f"admin_edit_redeem_amount_{rid}"
                ),

                InlineKeyboardButton(
                    "👥 Limit",
                    callback_data=f"admin_edit_redeem_limit_{rid}"
                )

            ],

            [

                InlineKeyboardButton(
                    "👤 Per User",
                    callback_data=f"admin_edit_redeem_per_user_{rid}"
                ),

                InlineKeyboardButton(
                    "📅 Expiry",
                    callback_data=f"admin_edit_redeem_expiry_{rid}"
                )

            ],

            [

                InlineKeyboardButton(
                    text="📋 Copy",
                    copy_text=CopyTextButton(
                        text=row["code"]
                    )
                ),

                InlineKeyboardButton(
                    "🗑 Delete",
                    callback_data=f"admin_delete_redeem_{rid}"
                )

            ],

            [

                InlineKeyboardButton(
                    "🟢 ON"
                    if row["status"] == 0
                    else "🔴 OFF",

                    callback_data=f"admin_toggle_redeem_{rid}"

                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="admin_redeem_list"
                ),

                InlineKeyboardButton(
                    "🏠 Admin",
                    callback_data="admin"
                )

            ]

        ])

    )

@route("admin_toggle_redeem")
async def admin_toggle_redeem(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    rid = int(
        query.data.replace(
            "admin_toggle_redeem_",
            ""
        )
    )

    cur.execute(
        """
        SELECT status
        FROM redeem
        WHERE id=?
        """,
        (rid,)
    )

    row = cur.fetchone()

    if not row:

        await query.answer(
            "❌ Redeem Not Found",
            show_alert=True
        )

        return

    status = 0 if row["status"] else 1

    cur.execute(
        """
        UPDATE redeem
        SET status=?
        WHERE id=?
        """,
        (
            status,
            rid
        )
    )

    db.commit()

    await query.answer(
        "✅ Updated"
    )

    query.data = (
        f"admin_redeem_info_{rid}"
    )

    await admin_redeem_info(
        update,
        context
    )

@route("admin_delete_redeem")
async def admin_delete_redeem(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    rid = int(
        query.data.replace(
            "admin_delete_redeem_",
            ""
        )
    )

    await edit(

        query,

"""⚠️ DELETE REDEEM

━━━━━━━━━━━━━━

Are you sure?

This action cannot be undone.
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "✅ Yes",
                    callback_data=f"admin_delete_redeem_yes_{rid}"
                ),

                InlineKeyboardButton(
                    "❌ No",
                    callback_data=f"admin_redeem_info_{rid}"
                )

            ],

            [

                InlineKeyboardButton(
                    "🏠 Admin",
                    callback_data="admin"
                )

            ]

        ])

    )

@route("admin_delete_redeem_yes")
async def admin_delete_redeem_yes(update: Update,
                                  context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    rid = int(
        query.data.replace(
            "admin_delete_redeem_yes_",
            ""
        )
    )

    cur.execute(
        """
        DELETE FROM redeem
        WHERE id=?
        """,
        (rid,)
    )

    db.commit()

    await query.answer(
        "✅ Deleted"
    )

    query.data = "admin_redeem_list"

    await admin_redeem_list(
        update,
        context
    )


async def refresh_redeem_info(
    context,
    chat_id,
    message_id,
    rid
):

    cur.execute(
        """
        SELECT *
        FROM redeem
        WHERE id=?
        """,
        (rid,)
    )

    row = cur.fetchone()

    if not row:

        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="❌ Redeem Not Found",
            reply_markup=redeem_back()
        )

        return

    remaining = max(
        0,
        row["limit_count"] - row["used_count"]
    )

    status = (
        "🟢 Active"
        if row["status"]
        else "🔴 Disabled"
    )

    expiry = (
        row["expire_at"]
        if row["expire_at"]
        else "Unlimited"
    )

    text = f"""🎁 REDEEM DETAILS

━━━━━━━━━━━━━━

🔑 Code
{row['code']}

💰 Amount
{row['amount']} Tk

👥 Limit
{row['limit_count']}

✅ Used
{row['used_count']}

📦 Remaining
{remaining}

👤 Per User
{row['per_user']}

📅 Expiry
{expiry}

📊 Status
{status}
"""

    keyboard = InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "💰 Amount",
                callback_data=f"admin_edit_redeem_amount_{rid}"
            ),

            InlineKeyboardButton(
                "👥 Limit",
                callback_data=f"admin_edit_redeem_limit_{rid}"
            )

        ],

        [

            InlineKeyboardButton(
                "👤 Per User",
                callback_data=f"admin_edit_redeem_per_user_{rid}"
            ),

            InlineKeyboardButton(
                "📅 Expiry",
                callback_data=f"admin_edit_redeem_expiry_{rid}"
            )

        ],

        [

            InlineKeyboardButton(
                "📋 Copy",
                callback_data=f"admin_copy_redeem_{rid}"
            ),

            InlineKeyboardButton(
                "🗑 Delete",
                callback_data=f"admin_delete_redeem_{rid}"
            )

        ],

        [

            InlineKeyboardButton(
                "🟢 ON" if row["status"] == 0 else "🔴 OFF",
                callback_data=f"admin_toggle_redeem_{rid}"
            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="admin_redeem_list"
            ),

            InlineKeyboardButton(
                "🏠 Admin",
                callback_data="admin"
            )

        ]

    ])

    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard
    )


async def save_admin_edit_redeem_amount(update: Update,
                                        context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    rid = value(uid, "edit_redeem_id")

    try:

        amount = int(update.message.text)

        if amount <= 0:
            raise ValueError

    except:

        await update.message.reply_text(
            "❌ Invalid Amount."
        )

        return

    cur.execute(
        """
        UPDATE redeem
        SET amount=?
        WHERE id=?
        """,
        (
            amount,
            rid
        )
    )

    db.commit()

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    msg = value(
        uid,
        "admin_redeem_msg"
    )

    await refresh_redeem_info(

        context,

        update.effective_chat.id,

        msg,

        rid

    )

async def save_admin_edit_redeem_limit(update: Update,
                                       context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    rid = value(uid, "edit_redeem_id")

    try:

        limit_count = int(update.message.text)

        if limit_count <= 0:
            raise ValueError

    except:

        await update.message.reply_text(
            "❌ Invalid Limit."
        )

        return

    cur.execute(
        """
        UPDATE redeem
        SET limit_count=?
        WHERE id=?
        """,
        (
            limit_count,
            rid
        )
    )

    db.commit()

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    msg = value(uid, "admin_redeem_msg")

    await refresh_redeem_info(

        context,

        update.effective_chat.id,

        msg,

        rid

    )

async def save_admin_edit_redeem_per_user(update: Update,
                                          context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    rid = value(uid, "edit_redeem_id")

    try:

        per_user = int(update.message.text)

        if per_user < 0:
            raise ValueError

    except:

        await update.message.reply_text(
            "❌ Invalid Value."
        )

        return

    cur.execute(
        """
        UPDATE redeem
        SET per_user=?
        WHERE id=?
        """,
        (
            per_user,
            rid
        )
    )

    db.commit()

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    msg = value(uid, "admin_redeem_msg")

    await refresh_redeem_info(

        context,

        update.effective_chat.id,

        msg,

        rid

    )

async def save_admin_edit_redeem_expiry(update: Update,
                                        context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    rid = value(uid, "edit_redeem_id")

    expiry = update.message.text.strip()

    if expiry.lower() == "none":

        expiry = None

    else:

        try:

            datetime.strptime(
                expiry,
                "%d-%m-%Y %H:%M"
            )

        except:

            await update.message.reply_text(
                "❌ Invalid Date."
            )

            return

    cur.execute(
        """
        UPDATE redeem
        SET expire_at=?
        WHERE id=?
        """,
        (
            expiry,
            rid
        )
    )

    db.commit()

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    msg = value(uid, "admin_redeem_msg")

    await refresh_redeem_info(

        context,

        update.effective_chat.id,

        msg,

        rid

    )


# ==========================
# REDEEM LIST
# ==========================

@route("admin_redeem_list")
async def admin_redeem_list(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT
            id,
            code,
            amount,
            status
        FROM redeem
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    if not rows:

        await edit(

            query,

            """📭 NO REDEEM FOUND""",

            redeem_back()

        )

        return

    keyboard = []

    for row in rows:

        icon = "🟢" if row["status"] else "🔴"

        keyboard.append([

            InlineKeyboardButton(

                f"{icon} {row['code']} • {row['amount']} Tk",

                callback_data=f"admin_redeem_info_{row['id']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(

            "🔍 Search",

            callback_data="admin_search_redeem"

        ),

        InlineKeyboardButton(

            "📊 Stats",

            callback_data="admin_redeem_stats"

        )

    ])

    keyboard.append([

        InlineKeyboardButton(

            "⬅️ Back",

            callback_data="admin_redeem_panel"

        ),

        InlineKeyboardButton(

            "🏠 Admin",

            callback_data="admin"

        )

    ])

    await edit(

        query,

        """🎁 REDEEM LIST

━━━━━━━━━━━━━━

Select a Redeem Code.
""",

        InlineKeyboardMarkup(keyboard)

    )

@route("admin_edit_redeem_per_user")
async def admin_edit_redeem_per_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    rid = int(
        query.data.replace(
            "admin_edit_redeem_per_user_",
            ""
        )
    )

    uid = update.effective_user.id

    set(uid, "edit_redeem_id", rid)

    set(
        uid,
        "admin_redeem_msg",
        query.message.message_id
    )

    start_input(
        uid,
        "admin_edit_redeem_per_user"
    )

    await edit(

        query,

        """👤 EDIT PER USER

━━━━━━━━━━━━━━

Send New Per User Limit

Example

1

0 = Unlimited
""",

        info_back(rid)

    )

@route("admin_edit_redeem_expiry")
async def admin_edit_redeem_expiry(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    rid = int(
        query.data.replace(
            "admin_edit_redeem_expiry_",
            ""
        )
    )

    uid = update.effective_user.id

    set(uid, "edit_redeem_id", rid)

    set(
        uid,
        "admin_redeem_msg",
        query.message.message_id
    )

    start_input(
        uid,
        "admin_edit_redeem_expiry"
    )

    await edit(

        query,

        """📅 EDIT EXPIRY

━━━━━━━━━━━━━━

Send New Expiry

Example

31-12-2026 23:59

or

none
""",

        info_back(rid)

    )



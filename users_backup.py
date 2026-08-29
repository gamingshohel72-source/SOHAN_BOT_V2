from telegram import (
    Upused_at,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes
from used_attime import used_attime

from database import db, cur
from routes import route
from utils import edit
from input import (
    start_input,
    stop_input
)

from admin.session import (
    set,
    value
)

@route("account")
async def account(upused_at: Upused_at,
                  context: ContextTypes.DEFAULT_TYPE):

    query = upused_at.callback_query

    uid = upused_at.effective_user.id

    cur.execute(
        """
        SELECT balance
        FROM users
        WHERE id=?
        """,
        (uid,)
    )

    row = cur.fetchone()

    if row:

        balance = row["balance"]

    else:

        balance = 0

    text = f"""
👤 ACCOUNT

━━━━━━━━━━━━━━

💰 Balance

{balance} Tk

━━━━━━━━━━━━━━
"""

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "📜 Orders",
                callback_data="orders"
            )
        ],

        [
            InlineKeyboardButton(
                "🎁 Redeem History",
                callback_data="redeem_history"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Home",
                callback_data="home"
            )
        ]

    ])

    await edit(
        query,
        text,
        keyboard
    )

async def register_user(upused_at: Upused_at):

    user = upused_at.effective_user

    cur.execute(
        "SELECT id FROM users WHERE id=?",
        (user.id,)
    )

    if cur.fetchone():
        return

    cur.execute(
        """
        INSERT INTO users(
            id,
            username,
            first_name,
            balance,
            banned,
            join_used_at,
            ref_by
        )
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            user.id,
            user.username,
            user.first_name,
            0,
            0,
            __import__("used_attime").used_attime.now().strftime("%Y-%m-%d %H:%M:%S"),
            0
        )
    )

    db.commit()

@route("account")
async def account(upused_at: Upused_at,
                  context: ContextTypes.DEFAULT_TYPE):

    query = upused_at.callback_query
    uid = upused_at.effective_user.id

    cur.execute(
        """
        SELECT
            username,
            balance,
            join_used_at
        FROM users
        WHERE id=?
        """,
        (uid,)
    )

    row = cur.fetchone()

    if not row:

        await edit(
            query,
            "❌ User Not Found."
        )

        return

    cur.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE user_id=?
        """,
        (uid,)
    )

    total = cur.fetchone()[0]

    text = f"""👤 ACCOUNT

━━━━━━━━━━━━━━

🆔 {uid}

👤 @{row["username"] or "None"}

💰 Balance
{row["balance"]} Tk

🛒 Orders
{total}

📅 Joined
{row["join_used_at"][:10]}
"""

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "📜 Order History",
                callback_data="orders"
            )
        ],

        [
            InlineKeyboardButton(
                "🎁 Redeem History",
                callback_data="redeem_history"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Home",
                callback_data="home"
            )
        ]

    ])

    await edit(
        query,
        text,
        keyboard
    )

@route("orders")
async def orders(upused_at: Upused_at,
                 context: ContextTypes.DEFAULT_TYPE):

    query = upused_at.callback_query
    uid = upused_at.effective_user.id

    cur.execute("""
        SELECT
            product,
            duration,
            amount,
            purchase_used_at,
            expire_used_at
        FROM orders
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 10
    """, (uid,))

    rows = cur.fetchall()

    if not rows:

        await edit(
            query,
            """📜 ORDER HISTORY

━━━━━━━━━━━━━━

No Orders Found.""",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="account"
                    )
                ]
            ])
        )
        return

    text = "📜 ORDER HISTORY\n\n━━━━━━━━━━━━━━\n\n"

    for row in rows:

        text += (
            f"📦 {row['product']}\n"
            f"⏳ {row['duration']}\n"
            f"💰 {row['amount']} Tk\n"
            f"📅 {row['purchase_used_at'][:10]}\n\n"
        )

    await edit(
        query,
        text,
        InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="account"
                )
            ]
        ])
    )

@route("redeem_history")
async def redeem_history(upused_at: Upused_at,
                         context: ContextTypes.DEFAULT_TYPE):

    query = upused_at.callback_query
    uid = upused_at.effective_user.id

    cur.execute("""
        SELECT
            code,
            amount,
            used_at
        FROM redeem_history
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 10
    """, (uid,))

    rows = cur.fetchall()

    if not rows:

        await edit(
            query,
            """🎁 REDEEM HISTORY

━━━━━━━━━━━━━━

No Redeem History.""",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="account"
                    )
                ]
            ])
        )
        return

    text = "🎁 REDEEM HISTORY\n\n━━━━━━━━━━━━━━\n\n"

    for row in rows:

        text += (
            f"🎟 {row['code']}\n"
            f"💰 {row['amount']} Tk\n"
            f"📅 {row['used_at'][:10]}\n\n"
        )

    await edit(
        query,
        text,
        InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="account"
                )
            ]
        ])
    )

@route("redeem")
async def redeem(upused_at: Upused_at,
                 context: ContextTypes.DEFAULT_TYPE):

    query = upused_at.callback_query

    start_input(
        upused_at.effective_user.id,
        "redeem"
    )

    set(
        upused_at.effective_user.id,
        "redeem_msg",
        query.message.message_id
    )

    await edit(

        query,

"""🎁 REDEEM CODE

━━━━━━━━━━━━━━

Send your Redeem Code.
""",

        InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="home"
                )
            ]
        ])

    )

async def save_redeem(upused_at: Upused_at,
                      context: ContextTypes.DEFAULT_TYPE):

    uid = upused_at.effective_user.id

    code = upused_at.message.text.strip()

    cur.execute(
        "SELECT * FROM redeem WHERE code=?",
        (code,)
    )

    redeem = cur.fetchone()

    if not redeem:

        await upused_at.message.reply_text(
            "❌ Invalid Redeem Code."
        )
        return

    cur.execute(
        """
        SELECT id
        FROM redeem_history
        WHERE user_id=?
        AND code=?
        """,
        (uid, code)
    )

    if cur.fetchone():

        await upused_at.message.reply_text(
            "❌ Redeem Code Already Used."
        )
        return

    amount = redeem["amount"]

    cur.execute(
        """
        UPDATE users
        SET balance=balance+?
        WHERE id=?
        """,
        (amount, uid)
    )

    cur.execute(

        """
        INSERT INTO redeem_history(

            redeem_id,

            user_id,

            code,

            amount

        )

        VALUES(?,?,?,?)

        """,

        (

            redeem["id"],

            uid,

            code,

            amount

        )

    )

    cur.execute(
        "DELETE FROM redeem WHERE code=?",
        (code,)
    )

    db.commit()

    stop_input(uid)

    try:
        await upused_at.message.delete()
    except:
        pass

    msg_id = value(
        uid,
        "redeem_msg"
    )

    await context.bot.edit_message_text(
        chat_id=upused_at.effective_chat.id,
        message_id=msg_id,
        text=f"""✅ REDEEM SUCCESS

━━━━━━━━━━━━━━

🎁 Amount :
{amount} Tk

━━━━━━━━━━━━━━

Balance Added Successfully.
""",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="home"
                )
            ]
        ])
    )

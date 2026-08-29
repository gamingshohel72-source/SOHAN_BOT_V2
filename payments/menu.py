from telegram import Update
from telegram.ext import ContextTypes

from routes import route
from .session import clear

from utils import edit

from .service import (
    methods,
    method,
    pending_payment
)

from .keyboard import (
    methods_keyboard,
    method_page,
    back_cancel,
    confirm
)

from .session import (
    create,
    set
)

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database import cur

@route("add_balance")
async def add_balance(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    uid = update.effective_user.id

    # Check pending payment
    if pending_payment(uid):

        await query.answer(
            "⚠️ You already have a pending payment.",
            show_alert=True
        )
        return

    # Create payment session
    create(uid)

    # Get payment methods
    rows = methods()

    print("ROWS =", rows)

    if not rows:

        await edit(
            query,
            """❌ No Payment Method Available

Please contact admin."""
        )
        return

    try:

        await edit(

            query,

            """💳 ADD BALANCE

━━━━━━━━━━━━━━

💰 Select Payment Method

Choose one of the payment methods below.

━━━━━━━━━━━━━━
""",

            methods_keyboard(rows)

        )

        print("ADD BALANCE PAGE OPENED")

    except Exception:

        import traceback
        traceback.print_exc()

async def payment_method(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    uid = update.effective_user.id

    mid = int(
        query.data.replace(
            "paymethod_",
            ""
        )
    )

    row = method(mid)

    if not row:

        await query.answer(
            "Payment Method Not Found",
            show_alert=True
        )
        return

    set(
        uid,
        "method",
        row["name"]
    )

    set(
        uid,
        "number",
        row["number"]
    )

    await edit(

        query,

f"""💳 PAYMENT

━━━━━━━━━━━━━━

Method :
{row["name"]}

━━━━━━━━━━━━━━

Number :

`{row["number"]}`

━━━━━━━━━━━━━━

📋 Copy the number above,
complete your payment,
then press Continue.
""",

        method_page(
            mid,
            row["number"]
        ),

        parse_mode="Markdown"

    )

async def payment_continue(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    uid = update.effective_user.id

    from input import start_input

    start_input(
        uid,
        "payment_amount"
    )

    await edit(

        query,

"""💰 ENTER AMOUNT

━━━━━━━━━━━━━━

Send your payment amount.

Example:

500
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="add_balance"
                ),

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="home"
                )

            ]

        ])

    )

async def payment_cancel(update, context):

    query = update.callback_query

    clear(update.effective_user.id)

    from input import stop_input

    stop_input(update.effective_user.id)

    from routes import open_page

    await open_page(
        update,
        context,
        "home"
    )

@route("rules")
async def rules(update, context):

    query = update.callback_query

    cur.execute(
        "SELECT value FROM settings WHERE key='rules'"
    )

    row = cur.fetchone()

    text = row["value"] if row else "❌ Rules not set."

    await edit(

        query,

f"""📜 RULES

━━━━━━━━━━━━━━

{text}
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

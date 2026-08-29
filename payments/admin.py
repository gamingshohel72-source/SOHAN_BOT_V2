from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import ContextTypes

from routes import route
from utils import edit
from input import start_input
from utils import edit
from routes import route

from .service import (
    pending,
    payment,
    approve as approve_service,
    reject,
    add_balance
)

from .keyboard import approve as approve_keyboard

from .keyboard import (
    approve,
    admin_back
)

from .session import (
    set,
    value
)

from input import (
    start_input,
    stop_input
)

from .session import (
    set,
    value
)

from .service import add_method

from .service import all_methods
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from .service import (
    method_by_id,
    delete_method,
    set_method_status
)

from .service import (
    update_method_name,
    update_method_number
)

from database import (
    db,
    cur
)

@route("payments")
async def payments(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    rows = pending()

    if not rows:

        await edit(

            query,

            """📭 NO PENDING PAYMENTS""",

            admin_back()

        )

        return

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(

                f"💳 #{row['id']} • {row['amount']} Tk",

                callback_data=f"pay_{row['id']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(

            "⬅️ Back",

            callback_data="admin"

        )

    ])

    await edit(

        query,

        """💳 PENDING PAYMENTS

━━━━━━━━━━━━━━

Select a payment request.
""",

        InlineKeyboardMarkup(keyboard)

    )

async def payment_details(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    pid = int(
        query.data.replace(
            "pay_",
            ""
        )
    )

    row = payment(pid)

    if not row:

        await edit(
            query,
            "❌ Payment Not Found."
        )

        return

    text = f"""💳 PAYMENT DETAILS

━━━━━━━━━━━━━━

🆔 ID
#{row['id']}

👤 User
{row['user']}

💳 Method
{row['method']}

💰 Amount
{row['amount']} Tk

🧾 TRX ID
{row['trxid']}

📊 Status
{row['status']}

━━━━━━━━━━━━━━

Choose an action below.
"""

    keyboard = InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "🖼 Screenshot",
                callback_data=f"photo_{pid}"
            )

        ],

        [

            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve_{pid}"
            ),

            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_{pid}"
            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="payments"
            )

        ]

    ])

    await edit(
        query,
        text,
        keyboard
    )
@route("photo")
async def payment_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    pid = int(query.data.replace("photo_", ""))

    row = payment(pid)

    if not row:

        await query.answer(
            "Payment Not Found",
            show_alert=True
        )
        return

    await context.bot.send_photo(

        chat_id=query.message.chat.id,

        photo=row["screenshot"],

        caption=f"""🖼 Payment Screenshot

━━━━━━━━━━━━━━

Payment ID : #{pid}
User : {row['user']}
Amount : {row['amount']} Tk"""

    )

    await query.answer()

@route("approve")
async def approve_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    pid = int(query.data.replace("approve_", ""))

    row = payment(pid)

    if not row:
        return

    approve_service(pid)

    add_balance(
        row["user"],
        row["amount"]
    )

    from logs import add_log

    add_log(
        admin_id=query.from_user.id,
        action="Approve Payment",
        details=f"Payment #{pid}"
    )

    try:

        await context.bot.send_message(

            chat_id=row["user"],

            text=f"""✅ Payment Approved

━━━━━━━━━━━━━━

Amount Added :
{row['amount']} Tk

Thank you."""

        )

    except:
        pass

    await edit(
        query,
        "✅ Payment Approved Successfully.",
        InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="payments"
                ),
                InlineKeyboardButton(
                    "🏠 Admin",
                    callback_data="admin"
                )
            ]
        ])
    )

@route("reject")
async def reject_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    pid = int(query.data.replace("reject_", ""))

    row = payment(pid)

    if not row:
        return

    reject(pid)

    from logs import add_log

    add_log(
        admin_id=query.from_user.id,
        action="Reject Payment",
        details=f"Payment #{pid}"
    )

    try:

        await context.bot.send_message(

            chat_id=row["user"],

            text="""❌ Payment Rejected

    Please contact support if you think this is a mistake."""

    )

    except:
        pass

@route("payment_logs")
async def payment_logs(update, context):

    query = update.callback_query

    await edit(
        query,
        "📝 Payment Logs\n\nNo logs available yet."
    )

from input import start_input

@route("add_method")
async def add_method(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    start_input(
        update.effective_user.id,
        "method_name"
    )

    await edit(

        query,

"""➕ ADD PAYMENT METHOD

━━━━━━━━━━━━━━

📝 Enter Method Name

Example:

"""

    )


from .session import set

async def save_method_name(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    name = update.message.text.strip()

    if not name:

        await update.message.reply_text(
            "❌ Invalid Method Name."
        )
        return

    set(
        uid,
        "new_method_name",
        name
    )

    start_input(
        uid,
        "method_number"
    )

    await update.message.reply_text(
"""📱 ENTER PAYMENT NUMBER

━━━━━━━━━━━━━━


"""
    )


async def save_method_number(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    number = update.message.text.strip()

    if not number:

        await update.message.reply_text(
            "❌ Invalid Number."
        )
        return

    name = value(
        uid,
        "new_method_name"
    )

    add_method(
        name,
        number
    )

    stop_input(uid)

    await update.message.reply_text(
f"""✅ PAYMENT METHOD ADDED

━━━━━━━━━━━━━━

💳 Name
➜ {name}

📱 Number
➜ {number}

━━━━━━━━━━━━━━

Successfully Added.
"""
    )

@route("manage_methods")
async def manage_methods(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    rows = all_methods()

    keyboard = []

    for row in rows:

        status = "🟢" if row["status"] else "🔴"

        keyboard.append([

            InlineKeyboardButton(
                f"{status} {row['name']}",
                callback_data=f"method_{row['id']}"
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="settings"
        )

    ])

    await edit(

        query,

"""📋 PAYMENT METHODS

━━━━━━━━━━━━━━

Select a method to manage.
""",

        InlineKeyboardMarkup(keyboard)

    )
@route("method")
async def method_page(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    mid = int(
        query.data.replace(
            "method_",
            ""
        )
    )

    row = method_by_id(mid)

    if not row:

        await query.answer(
            "Method Not Found",
            show_alert=True
        )
        return

    status = "🟢 Enabled" if row["status"] else "🔴 Disabled"

    keyboard = InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "✏️ Edit Name",
                callback_data=f"edit_method_name_{mid}"
            )

        ],

        [

            InlineKeyboardButton(
                "📱 Edit Number",
                callback_data=f"edit_method_number_{mid}"
            )

        ],

        [

            InlineKeyboardButton(
                "🔴 Disable" if row["status"] else "🟢 Enable",
                callback_data=f"toggle_method_{mid}"
            )

        ],

        [

            InlineKeyboardButton(
                "🗑 Delete",
                callback_data=f"delete_method_{mid}"
            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="manage_methods"
            )

        ]

    ])

    await edit(

        query,

f"""💳 PAYMENT METHOD

━━━━━━━━━━━━━━

Name
➜ {row["name"]}

Number
➜ `{row["number"]}`

Status
➜ {status}
""",

        keyboard,

        parse_mode="Markdown"

    )

async def delete_payment_method(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    mid = int(
        query.data.replace(
            "delete_method_",
            ""
        )
    )

    delete_method(mid)

    await query.answer(
        "✅ Method Deleted"
    )

    query.data = f"method_{mid}"

    await manage_methods(update, context)

async def toggle_payment_method(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    mid = int(
        query.data.replace(
            "toggle_method_",
            ""
        )
    )

    row = method_by_id(mid)

    if not row:

        await query.answer(
            "Method Not Found",
            show_alert=True
        )
        return

    status = 0 if row["status"] else 1

    set_method_status(
        mid,
        status
    )

    await query.answer(
        "✅ Updated"
    )

    row = method_by_id(mid)

    status = "🟢 Enabled" if row["status"] else "🔴 Disabled"

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "✏️ Edit Name",
                callback_data=f"edit_method_name_{mid}"
            )
        ],

        [
            InlineKeyboardButton(
                "📱 Edit Number",
                callback_data=f"edit_method_number_{mid}"
            )
        ],

        [
            InlineKeyboardButton(
                "🔴 Disable" if row["status"] else "🟢 Enable",
                callback_data=f"toggle_method_{mid}"
            )
        ],

        [
            InlineKeyboardButton(
                "🗑 Delete",
                callback_data=f"delete_method_{mid}"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="manage_methods"
            )
        ]

    ])

    await edit(

        query,

    f"""💳 PAYMENT METHOD

    ━━━━━━━━━━━━━━

    Name
    ➜ {row['name']}

    Number
    ➜ `{row['number']}`

    Status
    ➜ {status}
    """,

        keyboard,

        parse_mode="Markdown"

    )

async def edit_method_name(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    mid = int(query.data.replace("edit_method_name_", ""))

    set(update.effective_user.id, "edit_method_id", mid)

    start_input(update.effective_user.id, "edit_method_name")

    msg = await edit(

        query,

"""✏️ EDIT METHOD NAME

━━━━━━━━━━━━━━

Send New Method Name.
""",

        InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data=f"method_{mid}"
                ),
                InlineKeyboardButton(
                    "🏠 Admin Panel",
                    callback_data="admin"
                )
            ]
        ])

    )

    from .session import set_message

    if msg:
        set_message(update.effective_user.id, msg.message_id)

async def edit_method_number(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    mid = int(query.data.replace("edit_method_number_", ""))

    set(update.effective_user.id, "edit_method_id", mid)

    start_input(update.effective_user.id, "edit_method_number")

    msg = await edit(

        query,

"""📱 EDIT PAYMENT NUMBER

━━━━━━━━━━━━━━

Send New Number.
""",

        InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data=f"method_{mid}"
                ),
                InlineKeyboardButton(
                    "🏠 Admin Panel",
                    callback_data="admin"
                )
            ]
        ])

    )

    from .session import set_message

    if msg:
        set_message(update.effective_user.id, msg.message_id)

async def save_edit_method_name(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    mid = value(uid, "edit_method_id")

    row = method_by_id(mid)

    if not row:
        return

    old_name = row["name"]
    new_name = update.message.text.strip()

    update_method_name(mid, new_name)

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    from .session import message

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=message(uid),

        text=f"""✅ METHOD NAME UPDATED

━━━━━━━━━━━━━━

💳 Old Name
➜ {old_name}

🆕 New Name
➜ {new_name}

━━━━━━━━━━━━━━

✅ Updated Successfully.""",

        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data=f"method_{mid}"
                ),
                InlineKeyboardButton(
                    "🏠 Admin Panel",
                    callback_data="admin"
                )
            ]
        ])

    )


async def save_edit_method_number(update: Update,
                                  context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    mid = value(uid, "edit_method_id")

    row = method_by_id(mid)

    if not row:
        return

    old_number = row["number"]
    new_number = update.message.text.strip()

    update_method_number(mid, new_number)

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    from .session import message

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=message(uid),

        text=f"""✅ PAYMENT NUMBER UPDATED

━━━━━━━━━━━━━━

📞 Old Number
➜ {old_number}

📱 New Number
➜ {new_number}

━━━━━━━━━━━━━━

✅ Updated Successfully.""",

        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data=f"method_{mid}"
                ),
                InlineKeyboardButton(
                    "🏠 Admin Panel",
                    callback_data="admin"
                )
            ]
        ])

    )

@route("toggle_method")
async def toggle_method(update: Update,
                        context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    mid = int(query.data.replace("toggle_method_", ""))

    row = method_by_id(mid)

    if not row:
        await query.answer("Method Not Found", show_alert=True)
        return

    cur.execute(
        """
        UPDATE payment_methods
        SET status=?
        WHERE id=?
        """,
        (
            0 if row["status"] else 1,
            mid
        )
    )

    db.commit()

    await method_page(update, context)

@route("delete_method")
async def delete_method(update: Update,
                        context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    mid = int(query.data.replace("delete_method_", ""))

    cur.execute(
        "DELETE FROM payment_methods WHERE id=?",
        (mid,)
    )

    db.commit()

    await manage_methods(update, context)


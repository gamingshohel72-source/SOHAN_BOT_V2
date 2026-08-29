from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import ContextTypes
from utils import safe_delete
from .session import expired
from utils import edit

from input import start_input, stop_input
from utils import edit

from .session import (
    set,
    value,
    clear
)

from .keyboard import (
    back_cancel,
    confirm
)

from .service import (
    trx_exists,
    create_payment
)

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import ContextTypes

from input import start_input, stop_input
from utils import edit

from .session import (
    set,
    value,
    clear
)

from .keyboard import (
    back_cancel,
    confirm
)

from .service import (
    trx_exists,
    create_payment
)


async def payment_continue(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    uid = update.effective_user.id

    start_input(
        uid,
        "payment_amount"
    )

    msg = await edit(

        query,

"""💳 ADD BALANCE

━━━━━━━━━━━━━━

💰 Enter Payment Amount

""",

        back_cancel("add_balance")

    )

    if msg:

        from .session import set_message

        set_message(
            uid,
            msg.message_id
        )

async def save_amount(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    uid = update.effective_user.id

    try:

        amount = int(update.message.text)

        if amount <= 0:
            raise ValueError

    except:

        await update.message.delete()

        return

    await update.message.delete()

    set(uid, "amount", amount)

    stop_input(uid)

    start_input(
        uid,
        "payment_trx"
    )

    from .session import message

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=message(uid),

        text="""🧾 ENTER TRANSACTION ID

━━━━━━━━━━━━━━

Send your TRX ID.

""",

        reply_markup=back_cancel(
            "payment_continue"
        )

    )

async def save_trx(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    uid = update.effective_user.id

    trx = update.message.text.strip().upper()

    if len(trx) < 6:

        await update.message.delete()
        return

    if trx_exists(trx):

        await update.message.delete()
        return

    await update.message.delete()

    set(uid, "trx", trx)

    stop_input(uid)

    start_input(
        uid,
        "payment_photo"
    )

    from .session import message

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=message(uid),

        text="""📸 UPLOAD PAYMENT SCREENSHOT

━━━━━━━━━━━━━━

Send your payment screenshot.

Accepted:
• payment screenshot
""",

        reply_markup=back_cancel(
            "payment_continue"
        )

    )

async def save_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    uid = update.effective_user.id

    if not update.message.photo:

        await update.message.reply_text(
            "❌ Please send a payment screenshot."
        )

        return

    photo = update.message.photo[-1].file_id

    set(
        uid,
        "photo",
        photo
    )

    stop_input(uid)

    text = f"""✅ PAYMENT CONFIRMATION

━━━━━━━━━━━━━━

💳 Method
➜ {value(uid,"method")}

💰 Amount
➜ {value(uid,"amount")} Tk

🧾 TRX ID
➜ `{value(uid,"trx")}`

📸 Screenshot
➜ Received ✅

━━━━━━━━━━━━━━

Please verify all information.

Press Submit to send your payment request.
"""

    try:
        await update.message.delete()
    except:
        pass

    from .session import message

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=message(uid),

        text=text,

        parse_mode="Markdown",

        reply_markup=confirm()

    )

async def payment_submit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    uid = update.effective_user.id

    pid = create_payment(

        user=uid,

        method=value(uid, "method"),

        amount=value(uid, "amount"),

        trxid=value(uid, "trx"),

        screenshot=value(uid, "photo")

    )

    # Clear Session
    clear(uid)

    # Notify Admin
    try:

        from config import OWNER_ID

        await context.bot.send_photo(

            chat_id=OWNER_ID,

            photo=value(uid, "photo"),

            caption=f"""🔔 NEW PAYMENT REQUEST

━━━━━━━━━━━━━━

🆔 ID : #{pid}

👤 User : {uid}

💳 Method : {value(uid,'method')}

💰 Amount : {value(uid,'amount')} Tk

🧾 TRX ID :

{value(uid,'trx')}

━━━━━━━━━━━━━━

Open Admin → Payments
to Approve or Reject.
"""

        )

    except Exception as e:

        print(e)

    from .keyboard import home

    await edit(

        query,

        f"""✅ PAYMENT SUBMITTED

    ━━━━━━━━━━━━━━

    🆔 Request ID

    #{pid}

    ━━━━━━━━━━━━━━

    Your payment request has been sent successfully.

    ⏳ Please wait for admin approval.
    """,

        home()

    )

async def payment_back(update, context):

    query = update.callback_query

    uid = update.effective_user.id

    step = value(uid, "step")

    if step == "trx":

        await payment_continue(update, context)
        return

    if step == "photo":

        from input import start_input

        start_input(uid, "payment_trx")

        await edit(

            query,

"""🧾 ENTER TRX ID""",

            back_cancel("payment_continue")

        )


    if expired(uid):

        clear(uid)

        await update.message.reply_text(

            "⌛ Payment session expired."

        )

        return

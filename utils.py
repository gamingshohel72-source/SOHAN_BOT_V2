from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from collections import defaultdict
import asyncio
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import time

# ============ SEND ============

async def send(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text,
    keyboard=None,
    parse_mode=None
):

    if update.callback_query:

        return await update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard,
            parse_mode=parse_mode
        )

    return await update.message.reply_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=parse_mode
    )


# ============ EDIT ============

async def edit(
    query,
    text,
    keyboard=None,
    parse_mode=None
):

    if query is None:
        return

    try:

        await asyncio.sleep(0.2)

        return await query.edit_message_text(
            text=text,
            reply_markup=keyboard,
            parse_mode=parse_mode
        )

    except BadRequest as e:

        if "Message is not modified" in str(e):
            return

        raise

# ============ ANSWER ============

async def answer(
    query,
    text=None,
    alert=False
):

    from telegram.error import NetworkError
    import asyncio

    for attempt in range(3):

        try:

            await query.answer(
                text=text,
                show_alert=alert
            )

            return

        except NetworkError as e:

            if attempt == 2:
                print(
                    "⚠️ Callback answer network error:",
                    e
                )
                return

            await asyncio.sleep(
                1 + attempt
            )

# ============ DELETE ============

async def delete(
    context,
    chat_id,
    message_id
):

    try:

        await context.bot.delete_message(
            chat_id,
            message_id
        )

    except:

        pass

async def auto_delete(context, chat_id, message_id):

    await asyncio.sleep(AUTO_DELETE)

    try:

        await context.bot.delete_message(
            chat_id,
            message_id
        )

    except:

        pass

async def send_auto(
    update,
    context,
    text,
    keyboard=None,
    parse_mode=None
):

    if update.callback_query:

        msg = await update.callback_query.message.reply_text(
            text,
            reply_markup=keyboard,
            parse_mode=parse_mode
        )

    else:

        msg = await update.message.reply_text(
            text,
            reply_markup=keyboard,
            parse_mode=parse_mode
        )

    context.application.create_task(

        auto_delete(
            context,
            msg.chat.id,
            msg.message_id
        )

    )

    return msg


def back_button(page):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data=page
            )
        ]
    ])

_last_request = {}

def flood(user_id, delay=1):

    now = time.time()

    last = _last_request.get(user_id, 0)

    if now - last < delay:

        return True

    _last_request[user_id] = now

    return False

def chunk(data, size):

    for i in range(0, len(data), size):

        yield data[i:i + size]

async def safe_delete(message):

    try:
        await message.delete()
    except:
        pass

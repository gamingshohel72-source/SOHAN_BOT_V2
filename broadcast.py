from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import ContextTypes

from telegram.error import RetryAfter

import asyncio

from routes import route
from input import start_input, stop_input
from payments.session import set, value

from utils import edit

from database import db, cur


# =========================================================
# BROADCAST GLOBAL STATE
# =========================================================

BROADCAST_RUNNING = False
BROADCAST_STOP = False


# =========================================================
# PANEL HELPERS
# =========================================================

def save_panel(uid, query):

    set(
        uid,
        "bc_panel_chat",
        query.message.chat.id
    )

    set(
        uid,
        "bc_panel_msg",
        query.message.message_id
    )


def panel_chat(uid):

    return value(
        uid,
        "bc_panel_chat"
    )


def panel_message(uid):

    return value(
        uid,
        "bc_panel_msg"
    )


# =========================================================
# DELETE ADMIN INPUT
# =========================================================

async def delete_input_message(update):

    if not update.message:
        return

    try:
        await update.message.delete()
    except Exception:
        pass


# =========================================================
# BROADCAST MAIN MENU
# =========================================================

@route("broadcast")
async def broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    await query.answer()

    save_panel(
        uid,
        query
    )

    await edit(

        query,

"""📢 BROADCAST PANEL

━━━━━━━━━━━━━━

Select Message Type
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "📝 Text",
                    callback_data="bc_text"
                ),

                InlineKeyboardButton(
                    "🖼 Photo",
                    callback_data="bc_photo"
                )

            ],

            [

                InlineKeyboardButton(
                    "🎥 Video",
                    callback_data="bc_video"
                ),

                InlineKeyboardButton(
                    "🎞 Animation",
                    callback_data="bc_animation"
                )

            ],

            [

                InlineKeyboardButton(
                    "🎵 Audio",
                    callback_data="bc_audio"
                ),

                InlineKeyboardButton(
                    "🎤 Voice",
                    callback_data="bc_voice"
                )

            ],

            [

                InlineKeyboardButton(
                    "📄 Document",
                    callback_data="bc_document"
                )

            ],

            [

                InlineKeyboardButton(
                    "📜 History",
                    callback_data="bc_history"
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


# =========================================================
# TEXT
# =========================================================

@route("bc_text")
async def broadcast_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    await query.answer()

    save_panel(
        uid,
        query
    )

    set(
        uid,
        "bc_type",
        "text"
    )

    start_input(
        uid,
        "broadcast_text"
    )

    await edit(

        query,

"""📝 TEXT BROADCAST

━━━━━━━━━━━━━━

Send the message you want
to broadcast.

Your message will be deleted
automatically after receiving.

━━━━━━━━━━━━━━
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="broadcast"
                )

            ]

        ])

    )


# =========================================================
# PHOTO
# =========================================================

@route("bc_photo")
async def broadcast_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    await query.answer()

    save_panel(
        uid,
        query
    )

    set(
        uid,
        "bc_type",
        "photo"
    )

    start_input(
        uid,
        "broadcast_photo"
    )

    await edit(

        query,

"""🖼 PHOTO BROADCAST

━━━━━━━━━━━━━━

Send the photo.

Caption is optional.

Your photo will be deleted
automatically after receiving.

━━━━━━━━━━━━━━
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="broadcast"
                )

            ]

        ])

    )


# =========================================================
# VIDEO
# =========================================================

@route("bc_video")
async def broadcast_video(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    await query.answer()

    save_panel(
        uid,
        query
    )

    set(
        uid,
        "bc_type",
        "video"
    )

    start_input(
        uid,
        "broadcast_video"
    )

    await edit(

        query,

"""🎥 VIDEO BROADCAST

━━━━━━━━━━━━━━

Send the video.

Caption is optional.

Your video will be deleted
automatically after receiving.

━━━━━━━━━━━━━━
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="broadcast"
                )

            ]

        ])

    )


# =========================================================
# DOCUMENT
# =========================================================

@route("bc_document")
async def broadcast_document(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    await query.answer()

    save_panel(
        uid,
        query
    )

    set(
        uid,
        "bc_type",
        "document"
    )

    start_input(
        uid,
        "broadcast_document"
    )

    await edit(

        query,

"""📄 DOCUMENT BROADCAST

━━━━━━━━━━━━━━

Send the document.

Caption is optional.

Your document will be deleted
automatically after receiving.

━━━━━━━━━━━━━━
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="broadcast"
                )

            ]

        ])

    )


# =========================================================
# AUDIO
# =========================================================

@route("bc_audio")
async def broadcast_audio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    await query.answer()

    save_panel(
        uid,
        query
    )

    set(
        uid,
        "bc_type",
        "audio"
    )

    start_input(
        uid,
        "broadcast_audio"
    )

    await edit(

        query,

"""🎵 AUDIO BROADCAST

━━━━━━━━━━━━━━

Send the audio.

Caption is optional.

Your audio will be deleted
automatically after receiving.

━━━━━━━━━━━━━━
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="broadcast"
                )

            ]

        ])

    )


# =========================================================
# VOICE
# =========================================================

@route("bc_voice")
async def broadcast_voice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    await query.answer()

    save_panel(
        uid,
        query
    )

    set(
        uid,
        "bc_type",
        "voice"
    )

    start_input(
        uid,
        "broadcast_voice"
    )

    await edit(

        query,

"""🎤 VOICE BROADCAST

━━━━━━━━━━━━━━

Send the voice message.

Caption is optional.

Your voice message will be
deleted automatically.

━━━━━━━━━━━━━━
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="broadcast"
                )

            ]

        ])

    )


# =========================================================
# ANIMATION
# =========================================================

@route("bc_animation")
async def broadcast_animation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    await query.answer()

    save_panel(
        uid,
        query
    )

    set(
        uid,
        "bc_type",
        "animation"
    )

    start_input(
        uid,
        "broadcast_animation"
    )

    await edit(

        query,

"""🎞 ANIMATION BROADCAST

━━━━━━━━━━━━━━

Send the animation / GIF.

Caption is optional.

Your animation will be deleted
automatically after receiving.

━━━━━━━━━━━━━━
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="broadcast"
                )

            ]

        ])

    )

# =========================================================
# UNIVERSAL BROADCAST INPUT
# =========================================================

async def _receive_broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    media_type: str
):

    uid = update.effective_user.id
    message = update.message

    if not message:
        return

    file_id = None
    caption = message.caption or ""
    text = message.text or ""

    # -----------------------------------------
    # GET CONTENT
    # -----------------------------------------

    if media_type == "text":

        if not text:
            return

    elif media_type == "photo":

        if not message.photo:
            await delete_input_message(update)
            return

        file_id = message.photo[-1].file_id

    elif media_type == "video":

        if not message.video:
            await delete_input_message(update)
            return

        file_id = message.video.file_id

    elif media_type == "document":

        if not message.document:
            await delete_input_message(update)
            return

        file_id = message.document.file_id

    elif media_type == "audio":

        if not message.audio:
            await delete_input_message(update)
            return

        file_id = message.audio.file_id

    elif media_type == "voice":

        if not message.voice:
            await delete_input_message(update)
            return

        file_id = message.voice.file_id

    elif media_type == "animation":

        if not message.animation:
            await delete_input_message(update)
            return

        file_id = message.animation.file_id

    else:

        await delete_input_message(update)
        return

    # -----------------------------------------
    # DELETE ADMIN MESSAGE
    # -----------------------------------------

    await delete_input_message(update)

    # -----------------------------------------
    # STOP INPUT MODE
    # -----------------------------------------

    stop_input(uid)

    # -----------------------------------------
    # SAVE DRAFT
    # -----------------------------------------

    set(
        uid,
        "bc_draft_type",
        media_type
    )

    set(
        uid,
        "bc_draft_file",
        file_id
    )

    set(
        uid,
        "bc_draft_text",
        text
    )

    set(
        uid,
        "bc_draft_caption",
        caption
    )

    # -----------------------------------------
    # GET PANEL
    # -----------------------------------------

    chat_id = panel_chat(uid)
    message_id = panel_message(uid)

    if not chat_id or not message_id:
        return

    # -----------------------------------------
    # PREVIEW KEYBOARD
    # -----------------------------------------

    keyboard = InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "✏️ Edit",
                callback_data=f"bc_edit_{media_type}"
            ),

            InlineKeyboardButton(
                "🗑 Delete",
                callback_data=f"bc_delete_{media_type}"
            )

        ],

        [

            InlineKeyboardButton(
                "📤 Send Broadcast",
                callback_data=f"bc_confirm_{media_type}"
            )

        ],

        [

            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="broadcast"
            )

        ]

    ])

    # -----------------------------------------
    # PREVIEW TEXT
    # -----------------------------------------

    if media_type == "text":

        preview = f"""📝 TEXT BROADCAST

━━━━━━━━━━━━━━

👀 Preview

━━━━━━━━━━━━━━

{text}

━━━━━━━━━━━━━━

Ready to Send?
"""

    else:

        names = {

            "photo": "🖼 PHOTO",
            "video": "🎥 VIDEO",
            "document": "📄 DOCUMENT",
            "audio": "🎵 AUDIO",
            "voice": "🎤 VOICE",
            "animation": "🎞 ANIMATION"

        }

        title = names.get(
            media_type,
            media_type.upper()
        )

        preview = f"""{title} BROADCAST

━━━━━━━━━━━━━━

👀 Preview

━━━━━━━━━━━━━━

Caption:

{caption if caption else "No Caption"}

━━━━━━━━━━━━━━

Ready to Send?
"""

    # -----------------------------------------
    # EDIT PANEL
    # -----------------------------------------

    try:

        await context.bot.edit_message_text(

            chat_id=chat_id,

            message_id=message_id,

            text=preview,

            reply_markup=keyboard

        )

    except Exception as e:

        print(
            "BROADCAST PREVIEW ERROR:",
            e
        )

# =========================================================
# INPUT WRAPPERS
# =========================================================

async def send_text_broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await _receive_broadcast(
        update,
        context,
        "text"
    )


async def send_photo_broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await _receive_broadcast(
        update,
        context,
        "photo"
    )


async def send_video_broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await _receive_broadcast(
        update,
        context,
        "video"
    )


async def send_document_broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await _receive_broadcast(
        update,
        context,
        "document"
    )


async def send_audio_broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await _receive_broadcast(
        update,
        context,
        "audio"
    )


async def send_voice_broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await _receive_broadcast(
        update,
        context,
        "voice"
    )


async def send_animation_broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await _receive_broadcast(
        update,
        context,
        "animation"
    )


# =========================================================
# UNIVERSAL EDIT
# =========================================================

@route("bc_edit")
async def broadcast_edit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    data = query.data

    media_type = data.replace(
        "bc_edit_",
        "",
        1
    )

    allowed = {
        "text",
        "photo",
        "video",
        "document",
        "audio",
        "voice",
        "animation"
    }

    if media_type not in allowed:

        await query.answer(
            "❌ Invalid broadcast type.",
            show_alert=True
        )

        return

    await query.answer()

    set(
        uid,
        "bc_type",
        media_type
    )

    start_input(
        uid,
        "broadcast_" + media_type
    )

    names = {
        "text": "📝 Text",
        "photo": "🖼 Photo",
        "video": "🎥 Video",
        "document": "📄 Document",
        "audio": "🎵 Audio",
        "voice": "🎤 Voice",
        "animation": "🎞 Animation"
    }

    title = names[media_type]

    await edit(

        query,

f"""{title} BROADCAST — EDIT

━━━━━━━━━━━━━━

Send the new {media_type}.

The old draft will be replaced.

━━━━━━━━━━━━━━
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data=f"bc_preview_{media_type}"
                )

            ]

        ])

    )


# =========================================================
# UNIVERSAL DELETE
# =========================================================

@route("bc_delete")
async def broadcast_delete(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    data = query.data

    media_type = data.replace(
        "bc_delete_",
        "",
        1
    )

    allowed = {
        "text",
        "photo",
        "video",
        "document",
        "audio",
        "voice",
        "animation"
    }

    if media_type not in allowed:

        await query.answer(
            "❌ Invalid broadcast type.",
            show_alert=True
        )

        return

    await query.answer(
        "🗑 Draft deleted."
    )

    # Clear all draft data
    set(
        uid,
        "bc_draft_type",
        None
    )

    set(
        uid,
        "bc_draft_file",
        None
    )

    set(
        uid,
        "bc_draft_text",
        None
    )

    set(
        uid,
        "bc_draft_caption",
        None
    )

    stop_input(uid)

    await edit(

        query,

"""🗑 BROADCAST DRAFT DELETED

━━━━━━━━━━━━━━

The current draft has been
removed successfully.

━━━━━━━━━━━━━━
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "📢 New Broadcast",
                    callback_data="broadcast"
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


# =========================================================
# UNIVERSAL PREVIEW
# =========================================================

@route("bc_preview")
async def broadcast_preview(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    data = query.data

    media_type = data.replace(
        "bc_preview_",
        "",
        1
    )

    allowed = {
        "text",
        "photo",
        "video",
        "document",
        "audio",
        "voice",
        "animation"
    }

    if media_type not in allowed:

        await query.answer(
            "❌ Invalid broadcast type.",
            show_alert=True
        )

        return

    text = value(
        uid,
        "bc_draft_text"
    )

    caption = value(
        uid,
        "bc_draft_caption"
    )

    names = {
        "text": "📝 TEXT",
        "photo": "🖼 PHOTO",
        "video": "🎥 VIDEO",
        "document": "📄 DOCUMENT",
        "audio": "🎵 AUDIO",
        "voice": "🎤 VOICE",
        "animation": "🎞 ANIMATION"
    }

    title = names[media_type]

    if media_type == "text":

        if not text:

            await query.answer(
                "❌ Draft not found.",
                show_alert=True
            )

            return

        preview = f"""{title} BROADCAST

━━━━━━━━━━━━━━

👀 PREVIEW

━━━━━━━━━━━━━━

{text}

━━━━━━━━━━━━━━
"""

    else:

        file_id = value(
            uid,
            "bc_draft_file"
        )

        if not file_id:

            await query.answer(
                "❌ Media draft not found.",
                show_alert=True
            )

            return

        preview = f"""{title} BROADCAST

━━━━━━━━━━━━━━

👀 PREVIEW

━━━━━━━━━━━━━━

Caption:

{caption if caption else "No Caption"}

━━━━━━━━━━━━━━
"""

    await query.answer()

    await edit(

        query,

        preview,

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "✏️ Edit",
                    callback_data=f"bc_edit_{media_type}"
                ),

                InlineKeyboardButton(
                    "🗑 Delete",
                    callback_data=f"bc_delete_{media_type}"
                )

            ],

            [

                InlineKeyboardButton(
                    "📤 Send Broadcast",
                    callback_data=f"bc_confirm_{media_type}"
                )

            ],

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="broadcast"
                )

            ]

        ])

    )

# =========================================================
# UNIVERSAL CONFIRM
# =========================================================

@route("bc_confirm")
async def broadcast_confirm(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    media_type = query.data.replace(
        "bc_confirm_",
        "",
        1
    )

    allowed = {
        "text",
        "photo",
        "video",
        "document",
        "audio",
        "voice",
        "animation"
    }

    if media_type not in allowed:

        await query.answer(
            "❌ Invalid broadcast type.",
            show_alert=True
        )

        return

    # Check draft
    if media_type == "text":

        content = value(
            uid,
            "bc_draft_text"
        )

        if not content:

            await query.answer(
                "❌ Text draft not found.",
                show_alert=True
            )

            return

    else:

        content = value(
            uid,
            "bc_draft_file"
        )

        if not content:

            await query.answer(
                "❌ Media draft not found.",
                show_alert=True
            )

            return

    await query.answer()

    # Start broadcast
    await run_broadcast(
        query,
        context,
        uid,
        media_type
    )


# =========================================================
# SEND ONE MESSAGE
# =========================================================

async def _send_one(
    context,
    user_id,
    media_type,
    file_id=None,
    text=None,
    caption=None
):

    if media_type == "text":

        await context.bot.send_message(
            chat_id=user_id,
            text=text
        )

    elif media_type == "photo":

        await context.bot.send_photo(
            chat_id=user_id,
            photo=file_id,
            caption=caption or None
        )

    elif media_type == "video":

        await context.bot.send_video(
            chat_id=user_id,
            video=file_id,
            caption=caption or None
        )

    elif media_type == "document":

        await context.bot.send_document(
            chat_id=user_id,
            document=file_id,
            caption=caption or None
        )

    elif media_type == "audio":

        await context.bot.send_audio(
            chat_id=user_id,
            audio=file_id,
            caption=caption or None
        )

    elif media_type == "voice":

        await context.bot.send_voice(
            chat_id=user_id,
            voice=file_id,
            caption=caption or None
        )

    elif media_type == "animation":

        await context.bot.send_animation(
            chat_id=user_id,
            animation=file_id,
            caption=caption or None
        )


# =========================================================
# UNIVERSAL BROADCAST ENGINE
# =========================================================

async def run_broadcast(
    query,
    context,
    uid,
    media_type
):

    global BROADCAST_RUNNING
    global BROADCAST_STOP

    if BROADCAST_RUNNING:

        await query.answer(
            "⚠️ A broadcast is already running.",
            show_alert=True
        )

        return

    BROADCAST_RUNNING = True
    BROADCAST_STOP = False

    text = value(
        uid,
        "bc_draft_text"
    )

    file_id = value(
        uid,
        "bc_draft_file"
    )

    caption = value(
        uid,
        "bc_draft_caption"
    )

    try:

        cur.execute(
            """
            SELECT id
            FROM users
            """
        )

        users = cur.fetchall()

    except Exception as e:

        BROADCAST_RUNNING = False

        print(
            "BROADCAST USER QUERY ERROR:",
            e
        )

        await edit(
            query,
            "❌ Could not load users."
        )

        return

    total = len(users)

    success = 0
    failed = 0
    stopped = False

    await edit(

        query,

f"""⏳ BROADCAST STARTING

━━━━━━━━━━━━━━

Type:
{media_type.upper()}

Total:
{total}

━━━━━━━━━━━━━━

Please wait...
"""

    )

    for index, user in enumerate(
        users,
        start=1
    ):

        # -----------------------------------------
        # STOP CHECK
        # -----------------------------------------

        if BROADCAST_STOP:

            stopped = True

            break

        user_id = user["id"]

        try:

            await _send_one(

                context,
                user_id,
                media_type,
                file_id=file_id,
                text=text,
                caption=caption

            )

            success += 1

        except RetryAfter as e:

            try:

                await asyncio.sleep(
                    e.retry_after
                )

                if BROADCAST_STOP:

                    stopped = True

                    break

                await _send_one(

                    context,
                    user_id,
                    media_type,
                    file_id=file_id,
                    text=text,
                    caption=caption

                )

                success += 1

            except Exception:

                failed += 1

        except Exception as e:

            failed += 1

            print(
                "BROADCAST SEND ERROR:",
                e
            )

        # -----------------------------------------
        # PROGRESS
        # -----------------------------------------

        if (
            index % 20 == 0
            or index == total
        ):

            try:

                await context.bot.edit_message_text(

                    chat_id=query.message.chat.id,

                    message_id=query.message.message_id,

                    text=f"""📤 BROADCASTING

━━━━━━━━━━━━━━

Type:
{media_type.upper()}

Progress:
{index}/{total}

✅ Success:
{success}

❌ Failed:
{failed}

━━━━━━━━━━━━━━

🛑 Stop available
"""

                    ,
                    reply_markup=InlineKeyboardMarkup([

                        [

                            InlineKeyboardButton(
                                "🛑 Stop",
                                callback_data="bc_stop"
                            )

                        ]

                    ])

                )

            except Exception:

                pass

    # -----------------------------------------
    # FINISH
    # -----------------------------------------

    BROADCAST_RUNNING = False

    BROADCAST_STOP = False

    processed = success + failed

    if stopped:

        status = "🛑 BROADCAST STOPPED"

    else:

        status = "✅ BROADCAST COMPLETED"

    await context.bot.edit_message_text(

        chat_id=query.message.chat.id,

        message_id=query.message.message_id,

        text=f"""{status}

━━━━━━━━━━━━━━

📦 Type:
{media_type.upper()}

👥 Total:
{total}

📨 Processed:
{processed}

✅ Success:
{success}

❌ Failed:
{failed}

━━━━━━━━━━━━━━
"""

    )

    # -----------------------------------------
    # CLEAR DRAFT
    # -----------------------------------------

    set(
        uid,
        "bc_draft_type",
        None
    )

    set(
        uid,
        "bc_draft_file",
        None
    )

    set(
        uid,
        "bc_draft_text",
        None
    )

    set(
        uid,
        "bc_draft_caption",
        None
    )

    stop_input(uid)

    # -----------------------------------------
    # SAVE BROADCAST HISTORY
    # -----------------------------------------

    history_content = (
        text
        if media_type == "text"
        else file_id
    )

    save_broadcast_history(

        admin_id=uid,

        media_type=media_type,

        content=history_content,

        caption=caption,

        total=total,

        processed=processed,

        success=success,

        failed=failed,

        stopped=1 if stopped else 0

    )

# =========================================================
# STOP BROADCAST
# =========================================================

@route("bc_stop")
async def broadcast_stop(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    global BROADCAST_STOP

    query = update.callback_query

    if not BROADCAST_RUNNING:

        await query.answer(
            "No broadcast is running.",
            show_alert=True
        )

        return

    BROADCAST_STOP = True

    await query.answer(
        "🛑 Stopping broadcast..."
    )


# =========================================================
# BROADCAST HISTORY TABLE
# =========================================================

def ensure_broadcast_history():

    cur.execute("""
        CREATE TABLE IF NOT EXISTS broadcast_history(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            admin_id INTEGER,

            media_type TEXT,

            content TEXT,

            caption TEXT,

            total INTEGER DEFAULT 0,

            processed INTEGER DEFAULT 0,

            success INTEGER DEFAULT 0,

            failed INTEGER DEFAULT 0,

            stopped INTEGER DEFAULT 0,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP

        )
    """)

    db.commit()


# =========================================================
# SAVE HISTORY
# =========================================================

def save_broadcast_history(
    admin_id,
    media_type,
    content,
    caption,
    total,
    processed,
    success,
    failed,
    stopped
):

    ensure_broadcast_history()

    cur.execute(
        """
        INSERT INTO broadcast_history(

            admin,
            type,
            content,
            total,
            success,
            failed,
            created_at

        )

        VALUES(?,?,?,?,?,?,CURRENT_TIMESTAMP)
        """,

        (
            admin_id,
            media_type,
            content,
            total,
            success,
            failed
        )
    )

    db.commit()

    return cur.lastrowid

# =========================================================
# HISTORY LIST
# =========================================================

@route("bc_history")
async def broadcast_history(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    ensure_broadcast_history()

    cur.execute(
        """
        SELECT
            id,
            type,
            total,
            success,
            failed,
            created_at
        FROM broadcast_history
        ORDER BY id DESC
        LIMIT 10
        """
    )

    rows = cur.fetchall()

    if not rows:

        await edit(

            query,

"""📜 BROADCAST HISTORY

━━━━━━━━━━━━━━

No broadcast history found.

━━━━━━━━━━━━━━
""",

            InlineKeyboardMarkup([

                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="broadcast"
                    )
                ]

            ])

        )

        return


    text = """📜 BROADCAST HISTORY

━━━━━━━━━━━━━━

"""

    buttons = []


    for row in rows:

        status = (
            "🛑"
            if row["stopped"]
            else "✅"
        )


        text += (

            f"{status} #{row['id']}  "
            f"{row['media_type'].upper()}\n"

            f"   {row['success']}/{row['total']} "
            f"• {row['created_at']}\n\n"

        )


        buttons.append([

            InlineKeyboardButton(

                f"#{row['id']} "
                f"{row['media_type'].upper()}",

                callback_data=(
                    f"bc_history_{row['id']}"
                )

            )

        ])


    buttons.append([

        InlineKeyboardButton(

            "🗑 Clear History",

            callback_data="bc_history_clear"

        )

    ])


    buttons.append([

        InlineKeyboardButton(

            "⬅️ Back",

            callback_data="broadcast"

        )

    ])


    await edit(

        query,

        text,

        InlineKeyboardMarkup(
            buttons
        )

    )

# =========================================================
# HISTORY DETAILS
# =========================================================

@route("bc_history_")
async def broadcast_history_details(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    try:

        history_id = int(
            query.data.replace(
                "bc_history_",
                "",
                1
            )
        )

    except ValueError:

        await query.answer(
            "❌ Invalid history.",
            show_alert=True
        )

        return


    ensure_broadcast_history()


    cur.execute(
        """
        SELECT *
        FROM broadcast_history
        WHERE id=?
        LIMIT 1
        """,

        (history_id,)
    )


    row = cur.fetchone()


    if not row:

        await query.answer(
            "❌ History not found.",
            show_alert=True
        )

        return


    await query.answer()


    status = (

        "🛑 Stopped"

        if row["stopped"]

        else "✅ Completed"

    )


    await edit(

        query,

f"""📜 BROADCAST DETAILS

━━━━━━━━━━━━━━

🆔 ID:
#{row['id']}

📦 Type:
{row['media_type'].upper()}

📊 Status:
{status}

👥 Total:
{row['total']}

📨 Processed:
{row['processed']}

✅ Success:
{row['success']}

❌ Failed:
{row['failed']}

━━━━━━━━━━━━━━

📅 {row['created_at']}
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🔁 Resend",
                    callback_data=(
                        f"bc_resend_{row['id']}"
                    )
                )

            ],

            [

                InlineKeyboardButton(
                    "🗑 Delete",
                    callback_data=(
                        f"bc_history_delete_{row['id']}"
                    )
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ History",
                    callback_data="bc_history"
                )

            ]

        ])

    )

# =========================================================
# RESEND HISTORY
# =========================================================

@route("bc_resend")
async def broadcast_resend(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    try:

        history_id = int(
            query.data.replace(
                "bc_resend_",
                "",
                1
            )
        )

    except ValueError:

        await query.answer(
            "❌ Invalid history.",
            show_alert=True
        )

        return

    ensure_broadcast_history()

    cur.execute(
        """
        SELECT *
        FROM broadcast_history
        WHERE id=?
        LIMIT 1
        """,

        (history_id,)
    )

    row = cur.fetchone()

    if not row:

        await query.answer(
            "❌ Broadcast not found.",
            show_alert=True
        )

        return

    media_type = row["media_type"]

    # -----------------------------------------
    # RESTORE DRAFT
    # -----------------------------------------

    set(
        uid,
        "bc_draft_type",
        media_type
    )

    set(
        uid,
        "bc_draft_text",
        row["content"]
        if media_type == "text"
        else None
    )

    set(
        uid,
        "bc_draft_file",
        row["content"]
        if media_type != "text"
        else None
    )

    set(
        uid,
        "bc_draft_caption",
        row["caption"]
    )

    await query.answer(
        "🔁 Broadcast restored."
    )

    # -----------------------------------------
    # START AGAIN
    # -----------------------------------------

    await run_broadcast(

        query,
        context,
        uid,
        media_type

    )

# =========================================================
# SAFE BROADCAST STATE
# =========================================================

def broadcast_is_running():
    return BROADCAST_RUNNING


def broadcast_request_stop():
    global BROADCAST_STOP
    BROADCAST_STOP = True


# =========================================================
# CANCEL / CLEANUP
# =========================================================

@route("bc_cancel")
async def broadcast_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    stop_input(uid)

    set(uid, "bc_draft_type", None)
    set(uid, "bc_draft_file", None)
    set(uid, "bc_draft_text", None)
    set(uid, "bc_draft_caption", None)

    await query.answer("❌ Cancelled.")

    await edit(
        query,
        """❌ BROADCAST CANCELLED

━━━━━━━━━━━━━━

Draft removed.

━━━━━━━━━━━━━━
""",
        InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📢 Broadcast",
                    callback_data="broadcast"
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

# =========================================================
# DELETE ONE HISTORY
# =========================================================

@route("bc_history_delete")
async def broadcast_history_delete(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    uid = update.effective_user.id

    try:

        history_id = int(
            query.data.replace(
                "bc_history_delete_",
                "",
                1
            )
        )

    except ValueError:

        await query.answer(
            "❌ Invalid history.",
            show_alert=True
        )

        return

    ensure_broadcast_history()

    cur.execute(
        """
        DELETE FROM broadcast_history
        WHERE id=?
        """,
        (history_id,)
    )

    db.commit()

    await query.answer(
        "🗑 History deleted."
    )

    await broadcast_history(
        update,
        context
    )


# =========================================================
# CLEAR ALL HISTORY
# =========================================================

@route("bc_history_clear")
async def broadcast_history_clear(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    ensure_broadcast_history()

    cur.execute(
        """
        DELETE FROM broadcast_history
        """
    )

    db.commit()

    await query.answer(
        "🗑 All history deleted."
    )

    await broadcast_history(
        update,
        context
    )



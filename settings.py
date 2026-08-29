from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import ContextTypes

from routes import route

from utils import edit

from input import (
    start_input,
    stop_input
)

from database import (
    db,
    cur
)
from admin import has_permission
from payments.session import (
    set,
    value,
    set_message,
    message
)

def settings_buttons(back="settings"):

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data=back
            ),

            InlineKeyboardButton(
                "🏠 Admin Panel",
                callback_data="admin"
            )

        ],

        [

            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="settings"
            )

        ]

    ])

async def open_setting(

    query,

    uid,

    mode,

    title,

    placeholder

):

    cur.execute(
        "SELECT value FROM settings WHERE key=?",
        (mode,)
    )

    row = cur.fetchone()

    current = row["value"] if row else "Not Set"

    start_input(uid, mode)

    msg = await edit(

        query,

f"""{title}

━━━━━━━━━━━━━━

📄 Current Value

➜ {current}

━━━━━━━━━━━━━━

📝 {placeholder}
""",

        settings_buttons()

    )

    if msg:

        set_message(
            uid,
            msg.message_id
        )

@route("set_bot_name")
async def set_bot_name(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    await open_setting(
        update.callback_query,
        update.effective_user.id,
        "bot_name",
        "🤖 EDIT BOT NAME",
        "Send New Bot Name."
    )


@route("set_bonus")
async def set_bonus(update: Update,
                    context: ContextTypes.DEFAULT_TYPE):

    await open_setting(
        update.callback_query,
        update.effective_user.id,
        "join_bonus",
        "🎁 EDIT JOIN BONUS",
        "Send New Join Bonus."
    )


@route("set_support")
async def set_support(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    await open_setting(
        update.callback_query,
        update.effective_user.id,
        "support",
        "📞 EDIT SUPPORT",
        "Send Support Username."
    )


@route("set_channel")
async def set_channel(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    await open_setting(
        update.callback_query,
        update.effective_user.id,
        "channel",
        "📢 EDIT CHANNEL",
        "Send Channel Username."
    )


@route("set_rules")
async def set_rules(update: Update,
                    context: ContextTypes.DEFAULT_TYPE):

    await open_setting(
        update.callback_query,
        update.effective_user.id,
        "rules",
        "📜 EDIT RULES",
        "Send New Rules."
    )


@route("maintenance")
async def maintenance(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    await open_setting(
        update.callback_query,
        update.effective_user.id,
        "maintenance",
        "🔧 EDIT MAINTENANCE",
        "Send Maintenance Message."
    )


async def save_setting(update: Update,
                       context: ContextTypes.DEFAULT_TYPE,
                       key):

    uid = update.effective_user.id

    new_value = update.message.text.strip()

    cur.execute(
        "SELECT value FROM settings WHERE key=?",
        (key,)
    )

    row = cur.fetchone()

    old_value = row["value"] if row else "-"

    cur.execute(
        """
        UPDATE settings
        SET value=?
        WHERE key=?
        """,
        (
            new_value,
            key
        )
    )

    db.commit()

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    titles = {
        "bot_name": "🤖 BOT NAME",
        "join_bonus": "🎁 JOIN BONUS",
        "support": "📞 SUPPORT",
        "channel": "📢 CHANNEL",
        "rules": "📜 RULES",
        "maintenance": "🔧 MAINTENANCE"
    }

    title = titles.get(key, key.upper())

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=message(uid),

        text=setting_updated(
            title,
            old_value,
            new_value
        ),

        reply_markup=settings_buttons()

    )

SETTING_TITLES = {

    "bot_name": (
        "🤖 EDIT BOT NAME",
        "Send New Bot Name."
    ),

    "join_bonus": (
        "🎁 EDIT JOIN BONUS",
        "Send New Join Bonus."
    ),

    "support": (
        "📞 EDIT SUPPORT",
        "Send Support Username."
    ),

    "channel": (
        "📢 EDIT CHANNEL",
        "Send Channel Username."
    ),

    "rules": (
        "📜 EDIT RULES",
        "Send New Rules."
    ),

    "maintenance": (
        "🔧 EDIT MAINTENANCE",
        "Send Maintenance Message."
    )

}


def setting_updated(title, old_value, new_value):

    return f"""✅ {title} UPDATED

━━━━━━━━━━━━━━

📄 Old Value

➜ {old_value}

━━━━━━━━━━━━━━

🆕 New Value

➜ {new_value}

━━━━━━━━━━━━━━

✅ Updated Successfully."""

@route("settings")
async def settings(update: Update,
                   context: ContextTypes.DEFAULT_TYPE):

    if not has_permission(
        update.effective_user.id,
        "settings"
    ):

        await update.callback_query.answer(
            "❌ Access Denied",
            show_alert=True
        )
        return

    query = update.callback_query

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🤖 Bot Name",
                callback_data="set_bot_name"
            )
        ],

        [
            InlineKeyboardButton(
                "🎁 Join Bonus",
                callback_data="set_bonus"
            )
        ],

        [
            InlineKeyboardButton(
                "📞 Support",
                callback_data="set_support"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 Channel",
                callback_data="set_channel"
            )
        ],

        [
            InlineKeyboardButton(
                "📜 Rules",
                callback_data="set_rules"
            )
        ],

        [
            InlineKeyboardButton(
                "🔧 Maintenance",
                callback_data="maintenance"
            )
        ],

        [
            InlineKeyboardButton(
                "💳 Payment Methods",
                callback_data="manage_methods"
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
        "⚙️ SETTINGS",
        keyboard
    )

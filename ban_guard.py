from config import OWNER_ID
from database import is_banned
from input import stop_input

try:
    from cache import clear
except:
    def clear(uid):
        pass


async def ban_guard(update):

    uid = update.effective_user.id

    # Owner can never be banned
    if uid == OWNER_ID:
        return False

    if not is_banned(uid):
        return False

    stop_input(uid)

    try:
        clear(uid)
    except:
        pass

    text = (
        "⛔ ACCOUNT BANNED\n\n"
        "Your account has been permanently banned from this bot.\n\n"
        "🚫 You cannot use any feature.\n"
        "📩 Contact the bot owner if you think this is a mistake."
    )

    try:
        if update.callback_query:
            await update.callback_query.answer(
                text,
                show_alert=True
            )
        elif update.message:
            await update.message.reply_text(text)
    except:
        pass

    return True

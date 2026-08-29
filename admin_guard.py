from config import OWNER_ID
from database import is_admin


async def admin_guard(update):

    uid = update.effective_user.id

    # Owner সবসময় Allow
    if uid == OWNER_ID:
        return False

    # Admin হলে Allow
    if is_admin(uid):
        return False

    try:
        if update.callback_query:

            await update.callback_query.answer(
                "⛔ Your admin access has been revoked.",
                show_alert=True
            )

        elif update.message:

            await update.message.reply_text(
                "⛔ Your admin access has been revoked."
            )

    except:
        pass

    return True

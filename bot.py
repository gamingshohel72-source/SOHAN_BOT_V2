from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from telegram.ext import (
    MessageHandler,
    filters
)
from config import BOT_NAME
from admin_guard import admin_guard

from document import document_handler
from ban_guard import ban_guard
from backup import *

from config import *
from keyboards import *
from utils import *
from routes import ROUTES
from input import current_input
import traceback
from support import *
from logs import *
from database import *
from shop import *
from admin.admins import *

init_database()


from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running"

def web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=web).start()

# Modules
from users import *
from admin import *
from products import *
from keys import *
from api_keys import *
from payments import *
from broadcast import *
from settings import *
from backup import *

# ==========================
# START
# ==========================
@route("home")
async def start(update: Update,
                context: ContextTypes.DEFAULT_TYPE):

    if await ban_guard(update):

        return

    await register_user(update)

    user = update.effective_user
    user_first_name = user.first_name
    user_username = user.username or "No Username"
    user_id = user.id

    await send(
        update,
        context,
        f"""
🏠 {BOT_NAME}

━━━━━━━━━━━━━━

👋 Welcome {user_first_name}

👤NAME:
➜  @{user_username}

🆔UID:
➜ {user_id}

Choose an option below.
""",
        home_keyboard(update.effective_user.id)
    )

import traceback

async def error_handler(update, context):

    print("\n========== ERROR ==========")

    traceback.print_exception(
        type(context.error),
        context.error,
        context.error.__traceback__
    )

    print("===========================\n")

    try:
        if update and update.callback_query:
            await update.callback_query.answer(
                "⚠️ Something went wrong.",
                show_alert=True
            )
    except:
        pass

# ==========================
# CALLBACK
# ==========================

from routes import ROUTES, open_page

async def callback(update, context):

    if await ban_guard(update):

        return

    query = update.callback_query

    print(f"CALLBACK: {query.data}")

    await answer(query)

    data = query.data

    admin_routes = (
        "admin",
        "users",
        "settings",
        "backup",
        "broadcast",
        "payments",
        "logs",
        "products",
        "keys",
        "admin_list",
        "add_admin",
        "admin_info_",
        "admin_role",
        "remove_admin",
        "change_admin_role",
        "ban_user",
        "unban_user",
    )

    if any(data.startswith(x) for x in admin_routes):

        if await admin_guard(update):
            return

    if await ban_guard(update):
        return

    if data.startswith("duration:"):

        await product_confirm(update, context)

        return

    if flood(update.effective_user.id):

        await answer(
            update.callback_query,
            "Please wait...",
            True
        )

        return

    if data.startswith("prd_"):

        await product_duration(update, context)

        return

    if data == "buy_confirm":

        await buy_product(update, context)

        return

    if data.startswith("ubal_"):

        await admin_add_balance(update, context)

        return

    if data.startswith("admin_") and data[6:].isdigit():

        await admin_info(update, context)

        return

    if data.startswith("user_") and data[5:].isdigit():

        await user_info(update, context)

        return

    if data.startswith("del_support_"):

        await delete_support(update, context)

        return

    if data.startswith("del_channel_"):

        await delete_channel(
            update,
            context
        )

        return

    handled = await open_page(update, context, data)

    if handled:
        return

    if data == "product_on":

        await finish_product(update, context, "on")
        return

    if data == "product_off":

        await finish_product(update, context, "off")
        return

    if data == "edit_price":

        await edit_price(update, context)
        return

    if data == "edit_duration":

        await edit_duration(update, context)
        return

    if data == "edit_name":

        await edit_name(update, context)
        return

    if data.startswith("eprd_"):

        await edit_product_menu(update, context)

        return

    if data.startswith("dprd_"):

        await confirm_delete_product(update, context)
        return

    if data.startswith("delete_yes_"):

        await delete_product_confirm(update, context)
        return

    if data.startswith("keyprd_"):

        await key_duration(update, context)
        return

    if data.startswith("keydur_"):

        await key_input(update, context)

        return

    if data == "set_bot_name":
        await set_bot_name(update, context)
        return

    if data == "set_bonus":
        await set_bonus(update, context)
        return

    if data == "set_support":
        await set_support(update, context)
        return

    if data == "set_channel":
        await set_channel(update, context)
        return

    if data == "set_rules":
        await set_rules(update, context)
        return

    if data == "maintenance":
        await maintenance(update, context)
        return

        await maintenance(update, context)
        return

    if data == "settings_info":

        await settings_info(update, context)
        return

    if data == "reset_settings":

        await reset_settings(update, context)
        return

    if data == "create_backup":

        await create_backup(update, context)
        return

    if data == "restore_backup":

        await restore_backup(update, context)
        return

    if data.startswith("paymethod_"):

        await payment_method(update, context)

        return

    if data == "pay_continue":

        await payment_continue(update, context)

        return

    if data == "payment_continue":

        await payment_continue(update, context)

        return

    if data == "payment_submit":

        await payment_submit(update, context)

        return

    if data.startswith("pay_"):

        await payment_details(update, context)

        return

    if data.startswith("approve_"):

        await approve_payment(update, context)

        return

    if data.startswith("reject_"):

        await reject_payment(update, context)

        return

    if data == "payment_cancel":

        await payment_cancel(update, context)

        return

    if data == "payment_back":

        await payment_back(update, context)

        return

    if data == "admin":

        await dashboard(update, context)

        return

    if data == "users":

        await users(update, context)

        return

    if data == "bc_text":

        await broadcast_text(update, context)
        return

    if data == "bc_photo":

        await broadcast_photo(update, context)
        return

    if data == "bc_video":

        await broadcast_video(update, context)
        return

    if data == "bc_document":

        await broadcast_document(update, context)
        return

    if data == "bc_audio":

        await broadcast_audio(update, context)
        return

    if data == "bc_voice":

        await broadcast_voice(update, context)
        return

    if data == "bc_animation":

        await broadcast_animation(update, context)
        return

    if data == "home":

        await start(update, context)

        return

    if data.startswith("method_"):

        await method_page(update, context)

        return

    if data.startswith("delete_method_"):

        await delete_method(update, context)
        return

    if data.startswith("toggle_method_"):

        await toggle_method(update, context)
        return

    if data.startswith("edit_method_name_"):

        await edit_method_name(update, context)
        return

    if data.startswith("edit_method_number_"):

        await edit_method_number(update, context)
        return

    if data.startswith("ban_"):
        await ban_user(update, context)
        return

    if data.startswith("unban_"):
        await unban_user(update, context)
        return

# =========================================================
# INPUT TYPE VALIDATOR
# =========================================================

async def wrong_input(update, expected):

    message = update.message

    # Wrong message immediately delete
    if message:

        try:
            await message.delete()
        except Exception:
            pass

    names = {
        "text": "📝 Text message",
        "photo": "🖼 Photo",
        "video": "🎥 Video",
        "document": "📄 Document",
        "audio": "🎵 Audio",
        "voice": "🎤 Voice message",
        "animation": "🎞 Animation"
    }

    expected_name = names.get(
        expected,
        expected
    )

    alert = await update.effective_chat.send_message(

        f"""❌ WRONG COMMAND

━━━━━━━━━━━━━━

Please send:

{expected_name}

━━━━━━━━━━━━━━
"""
    )

    # Delete alert after 3 seconds
    await asyncio.sleep(3)

    try:
        await alert.delete()
    except Exception:
        pass


def get_message_type(message):

    if not message:
        return None

    if message.photo:
        return "photo"

    if message.video:
        return "video"

    if message.document:
        return "document"

    if message.audio:
        return "audio"

    if message.voice:
        return "voice"

    if message.animation:
        return "animation"

    if message.text:
        return "text"

    return None

async def input_handler(update: Update,
                        context: ContextTypes.DEFAULT_TYPE):

    if await ban_guard(update):

        return

    uid = update.effective_user.id
    mode = current_input(
        uid
    )

    # =====================================================
    # REMOTE API KEY MANAGER INPUT
    # =====================================================
    if mode and mode.startswith("api_keys_"):
        handled = await handle_api_key_input(update, context)
        if handled:
            return

    # =====================================================
    # WRONG INPUT PROTECTION
    # =====================================================

    expected_type = {

        "broadcast_text": "text",
        "broadcast_photo": "photo",
        "broadcast_video": "video",
        "broadcast_document": "document",
        "broadcast_audio": "audio",
        "broadcast_voice": "voice",
        "broadcast_animation": "animation"

    }.get(mode)

    if expected_type:

        actual_type = get_message_type(
            update.message
        )

        if actual_type != expected_type:

            await wrong_input(
                update,
                expected_type
            )

            return

    if await ban_guard(update):
        return

    elif mode == "search_user":

        print("MODE = search_user")

        await save_search_user(update, context)

        return

    elif mode == "redeem":

        await save_redeem(update, context)

        return

    elif mode == "broadcast":

        await send_broadcast(update, context)

        return

    elif mode == "add_balance":

        await save_balance(update, context)

        return

    elif mode == "add_admin":

        await save_add_admin(update, context)

        return

    elif mode == "keys":

        await save_keys(update, context)

        return

    elif mode == "search_key":

        await save_search_key(update, context)

        return

    elif mode == "remove_key":

        await save_remove_key(update, context)

        return

    elif mode == "bot_name":

        await save_setting(
            update,
            context,
            "bot_name"
        )
        return

    elif mode == "join_bonus":

        await save_setting(
            update,
            context,
            "join_bonus"
        )
        return

    elif mode == "support":

        await save_setting(
            update,
            context,
            "support"
        )
        return

    elif mode == "channel":

        await save_setting(
            update,
            context,
            "channel"
        )
        return

    elif mode == "rules":

        await save_setting(
            update,
            context,
            "rules"
        )
        return

    elif mode == "maintenance":

        await save_setting(
            update,
            context,
            "maintenance"
        )
        return

    elif mode == "payment_amount":

        await save_amount(update, context)

        return

    elif mode == "payment_trx":

        await save_trx(update, context)

        return

    elif mode == "payment_photo":

        await save_photo(update, context)

        return

    elif mode == "admin_balance":

        await save_admin_balance(update, context)

        return

    elif mode == "broadcast_text":

        await send_text_broadcast(update, context)
        return

    elif mode == "broadcast_photo":

        await send_photo_broadcast(update, context)
        return

    elif mode == "broadcast_video":

        await send_video_broadcast(update, context)
        return

    elif mode == "broadcast_document":

        await send_document_broadcast(update, context)
        return

    elif mode == "broadcast_audio":

        await send_audio_broadcast(update, context)
        return

    elif mode == "broadcast_voice":

        await send_voice_broadcast(update, context)
        return

    elif mode == "broadcast_animation":

        await send_animation_broadcast(update, context)
        return

    elif mode == "method_name":

        await save_method_name(update, context)

        return

    elif mode == "method_number":

        await save_method_number(update, context)

        return

    elif mode == "edit_method_name":

        await save_edit_method_name(update, context)
        return

    elif mode == "edit_method_number":

        await save_edit_method_number(update, context)
        return

    elif mode == "add_support":

        await save_add_support(
            update,
            context
        )

    elif mode == "add_channel":

        await save_add_channel(
            update,
            context
        )

    elif mode == "product_name":

        await save_product_name(update, context)

        return

    elif mode == "product_duration":

        await save_product_duration(update, context)

        return

    elif mode == "product_price":

        await save_product_price(update, context)

        return

    elif mode == "new_duration":

        await save_new_duration(update, context)

    elif mode == "new_price":

        await save_new_price(update, context)

    elif mode == "search_product":

        await save_search_product(
            update,
            context
        )

    elif mode == "save_keys":

        await save_keys(
            update,
            context
        )

        return


    elif mode == "generate_count":

        await save_generate_count(
            update,
            context
        )

        return


    elif mode == "import_txt":

        await import_txt(
            update,
            context
        )

        return


    elif mode == "search_key_value":

        await search_key_value(
            update,
            context
        )

        return


    elif mode == "search_buyer_value":

        await search_buyer_value(
            update,
            context
        )

        return


    elif mode == "search_order_value":

        await search_order_value(
            update,
            context
        )

        return


    elif mode == "search_product_duration":

        await search_product_duration(
            update,
            context
        )

        return

    elif mode == "edit_product":

        await save_edit_product(
            update,
            context
        )

        return

    elif mode == "add_product_name":

        await save_product_name(
            update,
            context
        )

        return


    elif mode == "add_product_duration":

        await save_product_duration(
            update,
            context
        )

        return


    elif mode == "add_product_price":

        await save_product_price(
            update,
            context
        )

        return


    elif mode == "add_duration":

        await save_product_duration(
            update,
            context
        )

        return


    elif mode == "edit_name":

        await save_edit_name(
            update,
            context
        )

        return


    elif mode == "edit_duration":

        await save_edit_duration(
            update,
            context
        )

        return


    elif mode == "edit_price":

        await save_edit_price(
            update,
            context
        )

        return


    elif mode == "search_product":

        await search_product_input(
            update,
            context
        )

        return

    elif mode == "backup_time":

        await save_backup_time(update, context)

        return

    elif mode == "admin_redeem_amount":

        await save_admin_redeem_amount(
            update,
            context
        )

    elif mode == "admin_redeem_limit":

        await save_admin_redeem_limit(
            update,
            context
        )

    elif mode == "admin_redeem_per_user":

        await save_admin_redeem_per_user(
            update,
            context
        )

    elif mode == "admin_redeem_expiry":

        await save_admin_redeem_expiry(
            update,
            context
        )

    elif mode == "admin_search_redeem":

        await save_admin_search_redeem(
            update,
            context
        )

    elif mode == "admin_edit_redeem_amount":

        await save_admin_edit_redeem_amount(
            update,
            context
        )

    elif mode == "admin_edit_redeem_limit":

        await save_admin_edit_redeem_limit(
            update,
            context
        )

    elif mode == "admin_edit_redeem_per_user":

        await save_admin_edit_redeem_per_user(
            update,
            context
        )

    elif mode == "admin_edit_redeem_expiry":

        await save_admin_edit_redeem_expiry(
            update,
            context
        )

    if current_input(uid) == "bc_text":

        set(
            uid,
            "bc_text",
            update.message.text
        )

        stop_input(uid)

        await update.message.reply_text(

            "✅ Saved"

        )

        return

    if current_input(uid) == "bc_photo":

        if not update.message.photo:

            await update.message.reply_text(
                "❌ Please send a photo."
            )
            return

        photo = update.message.photo[-1].file_id

        caption = update.message.caption or ""

        set(uid, "bc_photo", photo)
        set(uid, "bc_caption", caption)

        stop_input(uid)

        await update.message.reply_text(
            "✅ Photo Saved."
        )

        return

    elif mode == "api_search":

        await save_api_search(
            update,
            context
        )

        return

# ==========================
# MAIN
# ==========================

create_tables()

from telegram.request import HTTPXRequest

request = HTTPXRequest(
    connect_timeout=60,
    read_timeout=60,
    write_timeout=60,
    pool_timeout=60,
    connection_pool_size=20,
)

app = (
    Application.builder()
    .token(TOKEN)
    .request(request)
    .build()
)

app.add_handler(

    MessageHandler(

        filters.Document.ALL,

        document_handler

    )

)

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    CallbackQueryHandler(
        callback
    )
)

app.add_handler(
    MessageHandler(
        (
            filters.TEXT
            | filters.PHOTO
            | filters.VIDEO
            | filters.Document.ALL
            | filters.AUDIO
            | filters.VOICE
            | filters.ANIMATION
        ) & ~filters.COMMAND,
        input_handler
    )
)

app.add_error_handler(error_handler)

print(f"🤖 {BOT_NAME} Started Successfully")

app.run_polling(
    drop_pending_updates=True,
    allowed_updates=Update.ALL_TYPES
)

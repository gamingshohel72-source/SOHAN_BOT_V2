from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import ContextTypes

from routes import route
from utils import edit
from database import (
    db,
    cur
)

from payments.session import (
    set,
    value
)

from input import (
    start_input,
    stop_input
)

@route("backup")
async def backup(update: Update,
                 context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "📥 Create Backup",
                callback_data="create_backup"
            )
        ],

        [
            InlineKeyboardButton(
                "🕒 Auto Backup",
                callback_data="auto_backup"
            )
        ],

        [
            InlineKeyboardButton(
                "♻️ Restore Backup",
                callback_data="restore_backup"
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

"""📦 BACKUP PANEL

━━━━━━━━━━━━━━

Select an option below.

📥 Create a Full Backup

🕒 Configure Auto Backup

♻️ Restore Latest Backup
""",

        keyboard

    )

@route("auto_backup")
async def auto_backup(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute(
        "SELECT value FROM settings WHERE key='backup_enabled'"
    )

    row = cur.fetchone()

    enabled = (
        row is not None and
        row["value"] == "1"
    )

    cur.execute(
        "SELECT value FROM settings WHERE key='backup_time'"
    )

    row = cur.fetchone()

    backup_time = (
        row["value"]
        if row
        else "Not Set"
    )

    status = (
        "✅ Enabled"
        if enabled
        else "❌ Disabled"
    )

    keyboard = [

        [
            InlineKeyboardButton(
                "⏰ Change Time",
                callback_data="backup_time"
            )
        ]

    ]

    if enabled:

        keyboard.append([
            InlineKeyboardButton(
                "❌ Disable",
                callback_data="backup_disable"
            )
        ])

    else:

        keyboard.append([
            InlineKeyboardButton(
                "✅ Enable",
                callback_data="backup_enable"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="backup"
        )
    ])

    await edit(

        query,

f"""🕒 AUTO BACKUP

━━━━━━━━━━━━━━

Status : {status}

Time : {backup_time}

━━━━━━━━━━━━━━

Select an option.
""",

        InlineKeyboardMarkup(keyboard)

    )

@route("backup_time")
async def backup_time(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    from input import start_input

    start_input(
        update.effective_user.id,
        "backup_time"
    )

    set(
        update.effective_user.id,
        "backup_msg",
        query.message.message_id
    )

    await edit(

        query,

"""⏰ AUTO BACKUP TIME

━━━━━━━━━━━━━━

Send backup time in 24-hour format.

Example:

03:00
23:30
""",

        InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="auto_backup"
                )
            ]

        ])

    )

async def save_backup_time(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):

    from input import stop_input

    uid = update.effective_user.id

    text = update.message.text.strip()

    parts = text.split(":")

    if len(parts) != 2:

        await update.message.reply_text(
            "❌ Invalid format.\n\nExample: 03:00"
        )
        return

    try:

        hour = int(parts[0])
        minute = int(parts[1])

    except:

        await update.message.reply_text(
            "❌ Invalid time."
        )
        return

    if hour not in range(24) or minute not in range(60):

        await update.message.reply_text(
            "❌ Invalid time."
        )
        return

    cur.execute(
        """
        INSERT OR REPLACE INTO settings(
            key,
            value
        )
        VALUES(
            'backup_time',
            ?
        )
        """,
        (text,)
    )

    db.commit()

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    msg_id = value(uid, "backup_msg")

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=msg_id,
        text=f"""✅ AUTO BACKUP TIME SAVED

    ━━━━━━━━━━━━━━

    🕒 Time : {text}

    ━━━━━━━━━━━━━━

    Auto Backup Time Updated Successfully.
    """,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="auto_backup"
                )
            ]
        ])
    )

@route("backup_enable")
async def backup_enable(update: Update,
                        context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute(
        """
        INSERT OR REPLACE INTO settings(
            key,
            value
        )
        VALUES(
            'backup_enabled',
            '1'
        )
        """
    )

    db.commit()

    await query.answer(
        "✅ Auto Backup Enabled"
    )

    await auto_backup(update, context)

@route("backup_disable")
async def backup_disable(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute(
        """
        INSERT OR REPLACE INTO settings(
            key,
            value
        )
        VALUES(
            'backup_enabled',
            '0'
        )
        """
    )

    db.commit()

    await query.answer(
        "❌ Auto Backup Disabled"
    )

    await auto_backup(update, context)

import os
import zipfile
import asyncio
from datetime import datetime

BACKUP_FILE = "backup.zip"


async def auto_backup_worker():

    while True:

        try:

            cur.execute(
                "SELECT value FROM settings WHERE key='backup_enabled'"
            )

            row = cur.fetchone()

            if not row or row["value"] != "1":

                await asyncio.sleep(60)
                continue

            cur.execute(
                "SELECT value FROM settings WHERE key='backup_time'"
            )

            row = cur.fetchone()

            if not row:

                await asyncio.sleep(60)
                continue

            now = datetime.now().strftime("%H:%M")

            if now == row["value"]:

                if os.path.exists(BACKUP_FILE):
                    os.remove(BACKUP_FILE)

                with zipfile.ZipFile(
                    BACKUP_FILE,
                    "w",
                    zipfile.ZIP_DEFLATED
                ) as z:

                    if os.path.exists("database.db"):
                        z.write("database.db")

                    if os.path.exists("config.py"):
                        z.write("config.py")

                await asyncio.sleep(60)

        except Exception as e:

            print("AUTO BACKUP ERROR:", e)

        await asyncio.sleep(30)

import os
import zipfile

@route("create_backup")
async def create_backup(update: Update,
                        context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    BACKUP_FILE = "backup.zip"

    try:

        if os.path.exists(BACKUP_FILE):
            os.remove(BACKUP_FILE)

        with zipfile.ZipFile(
            BACKUP_FILE,
            "w",
            zipfile.ZIP_DEFLATED
        ) as z:

            items = [

                # Database
                "database.db",

                # Config
                "config.py",

                # Main Files
                "bot.py",
                "routes.py",
                "utils.py",
                "database.py",
                "input.py",
                "ban_guard.py",

                # Modules
                "shop.py",
                "keys.py",
                "products.py",
                "settings.py",
                "support.py",
                "broadcast.py",
                "document.py",

                # Folders
                "admin",
                "payments"

            ]

            for item in items:

                if not os.path.exists(item):
                    continue

                if os.path.isfile(item):

                    z.write(item)

                else:

                    for root, dirs, files in os.walk(item):

                        for file in files:

                            path = os.path.join(root, file)

                            z.write(path)

        with open(BACKUP_FILE, "rb") as backup:

            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=backup,
                filename="backup.zip",
                caption="✅ Full Backup Created Successfully"
            )

        await query.answer(
            "✅ Backup Created"
        )

    except Exception as e:

        print(e)

        await query.answer(
            "❌ Backup Failed",
            show_alert=True
        )

import os
import zipfile

@route("restore_backup")
async def restore_backup(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    BACKUP_FILE = "backup.zip"

    if not os.path.exists(BACKUP_FILE):

        await query.answer(
            "❌ Backup File Not Found",
            show_alert=True
        )
        return

    try:

        with zipfile.ZipFile(BACKUP_FILE, "r") as z:

            z.extractall(".")

        await edit(

            query,

"""♻️ BACKUP RESTORED

━━━━━━━━━━━━━━

✅ Database Restored

✅ Config Restored

━━━━━━━━━━━━━━

⚠️ Restart the bot to apply changes.
""",

            InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="backup"
                    )

                ]

            ])

        )

    except Exception as e:

        print(e)

        await query.answer(
            "❌ Restore Failed",
            show_alert=True
        )

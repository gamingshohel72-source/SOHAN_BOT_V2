from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import ContextTypes

from database import db, cur
from routes import route
from utils import edit


def add_log(admin_id, action, details=""):

    cur.execute(
        """
        INSERT INTO logs(
            admin_id,
            action,
            details
        )
        VALUES(?,?,?)
        """,
        (
            admin_id,
            action,
            details
        )
    )

    db.commit()


@route("logs")
async def logs(update: Update,
               context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT
            admin_id,
            action,
            details,
            date
        FROM logs
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cur.fetchall()

    text = "📋 ADMIN LOGS\n\n"

    if not rows:

        text += "No logs available yet."

    else:

        for row in rows:

            text += (
                f"👤 {row['admin_id']}\n"
                f"⚡ {row['action']}\n"
                f"📝 {row['details']}\n"
                f"🕒 {row['date']}\n\n"
            )

    await edit(

        query,

        text,

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🔄 Refresh",
                    callback_data="logs"
                ),

                InlineKeyboardButton(
                    "🗑 Clear",
                    callback_data="clear_logs"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="admin"
                ),

                InlineKeyboardButton(
                    "🏠 Admin Panel",
                    callback_data="admin"
                )

            ]

        ])

    )


@route("clear_logs")
async def clear_logs(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await edit(

        query,

"""⚠️ CLEAR ADMIN LOGS

━━━━━━━━━━━━━━

Are you sure you want to delete all admin logs?

❌ This action cannot be undone.
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "✅ Yes",
                    callback_data="confirm_clear_logs"
                ),

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="logs"
                )

            ]

        ])

    )


@route("confirm_clear_logs")
async def confirm_clear_logs(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute(
        "DELETE FROM logs"
    )

    db.commit()

    await query.answer(
        "✅ Logs Cleared Successfully."
    )

    await logs(update, context)

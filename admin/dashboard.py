from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import ContextTypes

from routes import route
from utils import edit
from database import cur


@route("statistics")
async def statistics(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products")
    products = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM keys")
    keys = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM payments WHERE status='pending'"
    )

    pending = cur.fetchone()[0]

    text = f"""📊 BOT STATISTICS

━━━━━━━━━━━━━━

👤 Users : {users}

🛒 Products : {products}

🔑 Keys : {keys}

💳 Pending Payments : {pending}
"""

    await edit(

        query,

        text,

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "📊 Dashboard",
                    callback_data="dashboard"
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


@route("dashboard")
async def dashboard(update: Update,
                    context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE banned=0")
    active_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE banned=1")
    banned_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM admins")
    total_admins = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM payments WHERE status='pending'"
    )
    pending_payments = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products")
    total_products = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM keys")
    total_keys = cur.fetchone()[0]

    await edit(

        query,

f"""📊 ADMIN DASHBOARD

━━━━━━━━━━━━━━

👥 Users : {total_users}

🟢 Active : {active_users}

🔴 Banned : {banned_users}

👮 Admins : {total_admins}

🛒 Products : {total_products}

🔑 Keys : {total_keys}

💳 Pending : {pending_payments}
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "👤 Users",
                    callback_data="users"
                ),

                InlineKeyboardButton(
                    "🛒 Products",
                    callback_data="products"
                )

            ],

            [

                InlineKeyboardButton(
                    "🔑 Keys",
                    callback_data="keys"
                ),

                InlineKeyboardButton(
                    "💳 Payments",
                    callback_data="payments"
                )

            ],

            [

                InlineKeyboardButton(
                    "🔄 Refresh",
                    callback_data="dashboard"
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



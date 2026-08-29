from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import ContextTypes

from routes import route
from utils import edit
from database import cur

@route("admin")
async def admin(update: Update,
                context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    keyboard = [

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
                "📢 Broadcast",
                callback_data="broadcast"
            ),

            InlineKeyboardButton(
                "🎁 Redeem",
                callback_data="admin_redeem_panel"
            )

        ],

        [
            InlineKeyboardButton(
                "⚙️ Settings",
                callback_data="settings"
            ),

            InlineKeyboardButton(
                "📊 Statistics",
                callback_data="statistics"
            )
        ],

        [

            InlineKeyboardButton(
                "🔐 API Keys",
                callback_data="api_keys"
            ),

            InlineKeyboardButton(
                "👑 Admin List",
                callback_data="admin_list"
            )
        ],

        [
            InlineKeyboardButton(
                "📞 Support Manager",
                callback_data="support_manager"
            ),

            InlineKeyboardButton(
                "👤 Add Admin",
                callback_data="add_admin"
            )
        ],

        [
            InlineKeyboardButton(
                "💾 Backup",
                callback_data="backup"
            ),

            InlineKeyboardButton(
                "📝 Logs",
                callback_data="logs"
            )
        ],

        [
            InlineKeyboardButton(
                "🏠 Home",
                callback_data="home"
            ),

            InlineKeyboardButton(
                "👥 All Users",
                callback_data="all_users"
            )
        ]

    ]

    await edit(

        query,

"""🛠 ADMIN PANEL

━━━━━━━━━━━━━━

Welcome Admin!

Select any option below.
""",

        InlineKeyboardMarkup(keyboard)

    )

def is_admin(user_id: int) -> bool:

    cur.execute(
        """
        SELECT 1
        FROM admins
        WHERE user_id=?
        LIMIT 1
        """,
        (user_id,)
    )

    return cur.fetchone() is not None


def admin_role(user_id: int):

    cur.execute(
        """
        SELECT role
        FROM admins
        WHERE user_id=?
        LIMIT 1
        """,
        (user_id,)
    )

    row = cur.fetchone()

    if row:

        return row["role"]

    return None


async def access_denied(update):

    query = update.callback_query

    await edit(

        query,

"""❌ ACCESS DENIED

━━━━━━━━━━━━━━

You are not authorized
to access the Admin Panel.
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🏠 Home",
                    callback_data="home"
                )

            ]

        ])

    )

@route("refresh_admin")
async def refresh_admin(update: Update,
                        context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(
        update.effective_user.id
    ):

        await access_denied(update)

        return

    await admin(
        update,
        context
    )

# ==========================
# PERMISSIONS
# ==========================

PERMISSIONS = {

    "premium": [
        "*"
    ],

    "owner": [
        "*"
    ],

    "manager": [

        "users",
        "products",
        "keys",
        "orders",
        "payments",
        "broadcast",
        "logs",
        "statistics"

    ],

    "support": [

        "users",
        "orders",
        "payments"

    ],

    "moderator": [

        "users",
        "keys"

    ],

    "normal": []

}


def has_permission(user_id,
                   permission):

    role = admin_role(user_id)

    if not role:

        return False

    perms = PERMISSIONS.get(
        role,
        []
    )

    if "*" in perms:

        return True

    return permission in perms

# ==========================
# REQUIRE PERMISSION
# ==========================

async def require_permission(update,
                             permission):

    uid = update.effective_user.id

    if not is_admin(uid):

        await access_denied(update)

        return False

    if not has_permission(
        uid,
        permission
    ):

        await edit(

            update.callback_query,

"""❌ PERMISSION DENIED

━━━━━━━━━━━━━━

You don't have permission
to access this section.
""",

            InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "⬅️ Admin Panel",
                        callback_data="admin"
                    )

                ]

            ])

        )

        return False

    return True

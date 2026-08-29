from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from admin.panel import admin_role

# ============ HOME ============

def home_keyboard(user_id):

    keyboard = [

        [
            InlineKeyboardButton("🛒 Shop", callback_data="shop"),
            InlineKeyboardButton("👤 Account", callback_data="account")
        ],

        [
            InlineKeyboardButton("💳 Add Balance", callback_data="add_balance"),
            InlineKeyboardButton("🎁 Redeem", callback_data="redeem")
        ],

        [
            InlineKeyboardButton("📞 Support", callback_data="support"),
            InlineKeyboardButton("📜Rules", callback_data="rules")
        ]

    ]

    # শুধুমাত্র Admin হলে Button দেখাবে
    if admin_role(user_id):

        keyboard.append([

            InlineKeyboardButton(
                "🛠 Admin",
                callback_data="admin"
            )

        ])

    return InlineKeyboardMarkup(keyboard)


# ============ BACK ============

def back(button="home"):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data=button
            )
        ]
    ])

# ============ YES / NO ============

def confirm(yes,no):

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "✅ Confirm",
                callback_data=yes
            ),

            InlineKeyboardButton(
                "❌ Cancel",
                callback_data=no
            )
        ]

    ])


# ============ ADMIN ============

def admin_keyboard():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton("👥 Users", callback_data="users"),
            InlineKeyboardButton("📦 Products", callback_data="products")
        ],

        [
            InlineKeyboardButton("🔑 Keys", callback_data="keys"),
            InlineKeyboardButton("💳 Payments", callback_data="payments")
        ],

        [
            InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
            InlineKeyboardButton("📊 Statistics", callback_data="statistics")
        ],

        [
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton("📁 Backup", callback_data="backup")
        ]

    ])

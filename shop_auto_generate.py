from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import ContextTypes

from routes import route
from database import cur, db
from utils import edit
from telegram import CopyTextButton
from api_keys import api_create_key

# =========================
# SHOP HOME
# =========================

@route("shop")
async def shop(update: Update,
               context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT DISTINCT name
        FROM products
        WHERE status='on'
        ORDER BY name ASC
    """)

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([
            InlineKeyboardButton(
                row["name"],
                callback_data=f"shop_group_{row['name']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🏠 Home",
            callback_data="home"
        )
    ])

    await edit(
        query,
        """🛒 SHOP

━━━━━━━━━━━━━━

Select a Product
""",
        InlineKeyboardMarkup(keyboard)
    )

# =========================
# SHOP GROUP
# =========================

@route("shop_group")
async def shop_group(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    print("SHOP GROUP OPEN")
    print("SHOP GROUP START")

    query = update.callback_query

    product = query.data.replace(
        "shop_group_",
        ""
    )

    print(product)

    cur.execute(
        """
        SELECT
            id,
            duration,
            price
        FROM products
        WHERE name=?
        AND status='on'
        ORDER BY id ASC
        """,
        (product,)
    )

    print("QUERY OK")

    rows = cur.fetchall()

    if not rows:

        await query.answer(
            "❌ Product not found.",
            show_alert=True
        )
        return

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(

                f"{row['duration']} • {row['price']} Tk",

                callback_data=f"shop_plan_{row['id']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="shop"
        ),

        InlineKeyboardButton(
            "🏠 Home",
            callback_data="home"
        )

    ])

    await edit(

        query,

f"""📦 {product}

━━━━━━━━━━━━━━

Select Duration
""",

        InlineKeyboardMarkup(
            keyboard
        )

    )

# =========================
# SHOP PLAN
# =========================

@route("shop_plan")
async def shop_plan(update: Update,
                    context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    plan_id = int(
        query.data.replace(
            "shop_plan_",
            ""
        )
    )

    cur.execute(
        """
        SELECT *
        FROM products
        WHERE id=?
        """,
        (plan_id,)
    )

    row = cur.fetchone()

    if not row:

        await query.answer(
            "❌ Product not found.",
            show_alert=True
        )
        return

    # Stock Count
    cur.execute(
        """
        SELECT COUNT(*)
        FROM keys
        WHERE product=?
        AND duration=?
        AND status='unused'
        """,
        (
            row["name"],
            row["duration"]
        )
    )

    stock = cur.fetchone()[0]

    keyboard = InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "🛒 Buy Now",
                callback_data=f"buy_{row['id']}"
            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data=f"shop_group_{row['name']}"
            ),

            InlineKeyboardButton(
                "🏠 Home",
                callback_data="home"
            )

        ]

    ])

    await edit(

        query,

f"""🛒 PRODUCT DETAILS

━━━━━━━━━━━━━━

📦 Product
{row['name']}

⏱ Duration
{row['duration']}

💰 Price
{row['price']} Tk

📦 Stock
{stock}

━━━━━━━━━━━━━━

Choose an option below.
""",

        keyboard

    )

# =========================
# BUY PRODUCT
# =========================

@route("buy")
async def buy_product(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    plan_id = int(
        query.data.replace(
            "buy_",
            ""
        )
    )

    cur.execute(
        """
        SELECT *
        FROM products
        WHERE id=?
        """,
        (plan_id,)
    )

    row = cur.fetchone()

    if not row:

        await query.answer(
            "❌ Product not found.",
            show_alert=True
        )
        return

    # User Balance
    cur.execute(
        """
        SELECT balance
        FROM users
        WHERE id=?
        """,
        (update.effective_user.id,)
    )

    user = cur.fetchone()

    balance = user["balance"] if user else 0

    await edit(

        query,

f"""🛒 CONFIRM PURCHASE

━━━━━━━━━━━━━━

📦 Product
{row['name']}

⏱ Duration
{row['duration']}

💰 Price
{row['price']} Tk

💳 Your Balance
{balance} Tk

━━━━━━━━━━━━━━

Do you want to continue?
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "✅ Confirm",
                    callback_data=f"confirm_buy_{plan_id}"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data=f"shop_plan_{plan_id}"
                ),

                InlineKeyboardButton(
                    "🏠 Home",
                    callback_data="home"
                )

            ]

        ])

    )

# =========================
# CONFIRM BUY
# =========================

@route("confirm_buy")
async def confirm_buy(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    uid = update.effective_user.id

    plan_id = int(
        query.data.replace(
            "confirm_buy_",
            ""
        )
    )

    # Product
    cur.execute(
        """
        SELECT *
        FROM products
        WHERE id=?
        """,
        (plan_id,)
    )

    product = cur.fetchone()

    if not product:

        await query.answer(
            "❌ Product not found.",
            show_alert=True
        )
        return

    # User
    cur.execute(
        """
        SELECT balance
        FROM users
        WHERE id=?
        """,
        (uid,)
    )

    user = cur.fetchone()

    if not user:

        await query.answer(
            "❌ User not found.",
            show_alert=True
        )
        return

    if user["balance"] < product["price"]:

        await query.answer(
            "❌ Insufficient Balance.",
            show_alert=True
        )
        return

    # Key delivery: STOCK FIRST -> AUTO GENERATE
    # The purchase handler is itself a @route("confirm_buy") route.
    order_no = ""
    result = api_create_key(
        product=product["name"],
        duration=product["duration"],
        order_id=order_no,
        customer_id=str(uid),
        buyer_id=uid
    )

    if not result.get("success"):
        await query.answer(
            "❌ Key generation failed. Payment was not deducted.",
            show_alert=True
        )
        await edit(
            query,
            f"""❌ KEY DELIVERY FAILED\n\n━━━━━━━━━━━━━━\n\n📦 Product\n{product['name']}\n\n⏱ Duration\n{product['duration']}\n\n❌ {result.get('error', 'Unknown error')}\n\nPlease try again later.""",
            InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Back", callback_data=f"buy_{plan_id}"),
                InlineKeyboardButton("🏠 Home", callback_data="home")
            ]])
        )
        return

    key_id = result["key_id"]
    key_value = result["key"]
    expire_at = result["expires_at"]

    # Balance Deduct -- only after a key was successfully reserved/generated
    cur.execute(
        "UPDATE users SET balance=balance-? WHERE id=?",
        (product["price"], uid)
    )

    # Save Order
    cur.execute(
        """
        INSERT INTO orders(
            user, product, duration, amount, key, status,
            purchase_date, product_id, key_id, created_at
        )
        VALUES(?, ?, ?, ?, ?, 'completed',
               datetime('now','localtime'), ?, ?,
               datetime('now','localtime'))
        """,
        (
            uid, product["name"], product["duration"], product["price"],
            key_value, product["id"], key_id
        )
    )

    db.commit()

    await edit(

        query,

f"""✅ PURCHASE SUCCESS

━━━━━━━━━━━━━━

📦 Product
{product['name']}

⏱ Duration
{product['duration']}

💰 Paid
{product['price']} Tk

🔑 Your Key

━━━━━━━━━━━━━━
{key_value}
━━━━━━━━━━━━━━

━━━━━━━━━━━━━━

Thank you for shopping ❤️
""",

    InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                text="📋 Copy Key",
                copy_text=CopyTextButton(
                    text=key_value
                )
            )

        ],

        [

            InlineKeyboardButton(
                "🛒 Shop",
                callback_data="shop"
            ),

            InlineKeyboardButton(
                "🏠 Home",
                callback_data="home"
            )

        ]

    ])


)

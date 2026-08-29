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
from datetime import datetime, timedelta
import asyncio
from config import KEY_API_SECRET, KEY_API_URL

# =========================
# WEBSITE KEY API CLIENT
# =========================

import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def _api_secret():
    try:
        from config import KEY_API_SECRET
        return KEY_API_SECRET.strip().replace("\ufeff", "")
    except Exception:
        return ""

def _api_request(method, path, payload=None, timeout=12):

    try:
        from config import KEY_API_URL, KEY_API_SECRET
    except Exception:
        return {
            "success": False,
            "error": "Config not found"
        }, 0


    base = KEY_API_URL.strip().rstrip("/")

    secret = KEY_API_SECRET.strip().replace("\ufeff", "")


    if not secret:
        return {
            "success": False,
            "error": "API secret not configured"
        }, 0


    try:
        secret.encode("ascii")

    except UnicodeEncodeError:
        return {
            "success": False,
            "error": "API secret contains invalid characters"
        }, 0


    body = None

    if payload is not None:
        body = json.dumps(
            payload,
            ensure_ascii=True
        ).encode("utf-8")


    req = Request(
        base + path,
        data=body,
        method=method.upper(),
        headers={
            "Authorization": "Bearer " + secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )


    try:

        with urlopen(req, timeout=timeout) as resp:

            raw = resp.read().decode(
                "utf-8",
                errors="replace"
            )

            return (
                json.loads(raw) if raw else {},
                resp.status
            )


    except HTTPError as exc:

        try:
            raw = exc.read().decode(
                "utf-8",
                errors="replace"
            )

            data = json.loads(raw) if raw else {}

        except Exception:

            data = {
                "success": False,
                "error": f"http_{exc.code}"
            }


        return data, exc.code


    except (URLError, TimeoutError, OSError) as exc:

        return {
            "success": False,
            "error": f"api_unreachable: {exc}"
        }, 0


def _api_generate(product, duration, order_id="", customer_id=""):

    return _api_request(
        "POST",
        "/generate",
        {
            "product": str(product),
            "duration": str(duration),
            "order_id": str(order_id),
            "customer_id": str(customer_id),
        }
    )



def _api_delete(key):

    return _api_request(
        "DELETE",
        "/keys/" + str(key)
    )

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

    for percent, bar in [
        (10, "▓░░░░░░░░░"),
        (30, "▓▓▓░░░░░░░"),
        (60, "▓▓▓▓▓▓░░░░"),
        (90, "▓▓▓▓▓▓▓▓▓░"),
        (100,"▓▓▓▓▓▓▓▓▓▓")
    ]:

        await edit(
            query,
            f"""╭━━ Processing... ━━╮

    🔍 Checking Stock...

    [{bar}] {percent}%

    ╰━━━━━━━━━━━━━━━━━━╯"""
        )

        await asyncio.sleep(0.5)

    # =====================================================
    # DELIVERY: BOT STOCK FIRST -> WEBSITE API FALLBACK
    # =====================================================
    cur.execute(
        """
        SELECT * FROM keys
        WHERE product=? AND duration=? AND status='unused'
        ORDER BY id ASC LIMIT 1
        """,
        (product["name"], product["duration"]),
    )
    key = cur.fetchone()

    api_created = False
    api_order_id = "GH" + datetime.now().strftime("%y%m%d%H%M%S") + str(uid)[-4:]
    api_expire_at = None

    if key:

        await edit(
            query,
            """╭━━ Processing... ━━╮

    ✅ Stock Found

    📦 Taking key from stock...

    ╰━━━━━━━━━━━━━━━━━━╯"""
       )

        await asyncio.sleep(1)

    else:

        await edit(
            query,
            """╭━━ Processing... ━━╮

    ⚠️ Stock Empty

    🌐 Calling API...

    ╰━━━━━━━━━━━━━━━━━━╯"""
        )

        await asyncio.sleep(2)

    if not key:
        # IMPORTANT: no local stock is NOT an OUT-OF-STOCK result.
        # Ask the real website API to generate the key.
        api_data, api_status = _api_generate(
            product["name"],
            product["duration"],
            api_order_id,
            str(uid),
        )
        if not api_data.get("success") or not api_data.get("key"):
            reason = api_data.get("error", f"API HTTP {api_status}")
            await query.answer("❌ API GENERATION FAILED", show_alert=True)
            await edit(
                query,
                f"""❌ KEY DELIVERY FAILED\n\n━━━━━━━━━━━━━━\n\n📦 Product\n{product['name']}\n\n⏱ Duration\n{product['duration']}\n\n🌐 API\n❌ {reason}\n\nYour balance was NOT deducted.""",
                InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Back", callback_data=f"buy_{plan_id}"),
                    InlineKeyboardButton("🏠 Home", callback_data="home"),
                ]]),
            )
            return

        # API is the source of truth for this generated key. Do NOT insert
        # it into the bot's local `keys` stock table.
        key = {
            "id": None,
            "key": api_data["key"],
            "expires_at": api_data.get("expires_at"),
        }
        api_created = True
        api_expire_at = api_data.get("expires_at")

    await edit(
        query,
        """╭━━ Processing... ━━╮

    🔐 Generating Key...

    ▓▓▓▓▓▓▓▓▓▓ 100%

    ╰━━━━━━━━━━━━━━━━━━╯"""
    )

    await asyncio.sleep(1)

    # Balance Deduct
    cur.execute(
        """
        UPDATE users
        SET balance=balance-?
        WHERE id=?
        """,
        (
            product["price"],
            uid
        )
    )

    days = 0

    duration = product["duration"].lower()

    if duration == "1day":
        days = 1
    elif duration == "3day":
        days = 3
    elif duration == "7day":
        days = 7
    elif duration == "15day":
        days = 15
    elif duration == "30day":
        days = 30

    expire_at = None

    if days > 0:
        expire_at = (
            datetime.now() +
            timedelta(days=days)
        ).strftime("%Y-%m-%d %H:%M:%S")

    # Mark only BOT-stock keys as used. API-generated keys live in the
    # website API database and must not be duplicated into local stock.
    if not api_created:
        cur.execute(
            """
            UPDATE keys
            SET status='used', buyer_id=?, used_at=datetime('now','localtime'), expire_at=?
            WHERE id=?
            """,
            (uid, expire_at, key["id"]),
        )
    else:
        expire_at = api_expire_at or expire_at

    # Save Order
    cur.execute(
        """
        INSERT INTO orders(
            user,
            product,
            duration,
            amount,
            key,
            status,
            purchase_date,
            product_id,
            key_id,
            created_at
        )
        VALUES(
            ?, ?, ?, ?, ?, 'completed',
            datetime('now','localtime'),
            ?, ?,
            datetime('now','localtime')
        )
        """,
        (
            uid,
            product["name"],
            product["duration"],
            product["price"],
            key["key"],
            product["id"],
            None if api_created else key["id"]
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
{key['key']}
━━━━━━━━━━━━━━

━━━━━━━━━━━━━━

Thank you for shopping ❤️
""",

    InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                text="📋 Copy Key",
                copy_text=CopyTextButton(
                    text=key["key"]
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

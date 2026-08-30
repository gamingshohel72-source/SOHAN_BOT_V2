from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    ContextTypes
)

from routes import route

from database import (
    db,
    cur
)

from utils import (
    edit,
    answer
)

from input import (
    start_input,
    stop_input
)

from payments.session import (
    set,
    value,
    clear
)

# ==========================
# PRODUCTS
# ==========================

PRODUCTS_PER_PAGE = 15

# ==========================
# HELPERS
# ==========================


async def delete_input(update):

    try:

        await update.message.delete()

    except:

        pass


def back_admin():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="products"
            ),

            InlineKeyboardButton(
                "🏠 Admin",
                callback_data="admin"
            )

        ]

    ])


def success_keyboard():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "📦 Product List",
                callback_data="product_list"
            )

        ],

        [

            InlineKeyboardButton(
                "➕ Add Product",
                callback_data="add_product"
            )

        ],

        [

            InlineKeyboardButton(
                "🏠 Admin",
                callback_data="admin"
            )

        ]

    ])

def details_keyboard():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "✏️ Edit",
                callback_data="edit_product"
            ),

            InlineKeyboardButton(
                "🔄 ON/OFF",
                callback_data="toggle_product"
            )

        ],

        [

            InlineKeyboardButton(
                "🗑 Delete",
                callback_data="delete_product"
            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="product_group"
            ),

            InlineKeyboardButton(
                "🏠 Admin",
                callback_data="admin"
            )

        ]

    ])


def delete_keyboard():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "✅ Yes",
                callback_data="delete_product_yes"
            ),

            InlineKeyboardButton(
                "❌ No",
                callback_data="product_info"
            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="product_info"
            )

        ]

    ])

# ==========================
# PRODUCT MENU
# ==========================

@route("products")
async def products(update: Update,
                   context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""

        SELECT COUNT(DISTINCT name)

        FROM products

    """)

    total_products = cur.fetchone()[0]

    cur.execute("""

        SELECT COUNT(*)

        FROM products

        WHERE status='on'

    """)

    total_active = cur.fetchone()[0]

    cur.execute("""

        SELECT COUNT(*)

        FROM products

        WHERE status='off'

    """)

    total_disabled = cur.fetchone()[0]

    set(

        update.effective_user.id,

        "product_page",

        0

    )

    await edit(

        query,

f"""📦 PRODUCT MANAGER

━━━━━━━━━━━━━━

📦 Products : {total_products}

🟢 Active Plans : {total_active}

🔴 Disabled Plans : {total_disabled}

━━━━━━━━━━━━━━

Select an option.
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(

                    "📦 Product List",

                    callback_data="product_list"

                )

            ],

            [

                InlineKeyboardButton(

                    "➕ Add Product",

                    callback_data="add_product"

                ),

                InlineKeyboardButton(

                    "🔍 Search",

                    callback_data="search_product"

                )

            ],

            [

                InlineKeyboardButton(

                    "⬅️ Back",

                    callback_data="admin"

                ),

                InlineKeyboardButton(

                    "🏠 Home",

                    callback_data="home"

                )

            ]

        ])

    )

# ==========================
# PRODUCT LIST
# ==========================

@route("product_list")
async def product_list(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    uid = update.effective_user.id

    page = value(

        uid,

        "product_page"

    ) or 0

    limit = PRODUCTS_PER_PAGE

    offset = page * limit

    cur.execute("""

        SELECT COUNT(DISTINCT name)

        FROM products

    """)

    total = cur.fetchone()[0]

    cur.execute("""

        SELECT

            name,

            COUNT(*) AS plans

        FROM products

        GROUP BY name

        ORDER BY name COLLATE NOCASE

        LIMIT ?

        OFFSET ?

    """,

    (

        limit,

        offset

    ))

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(

                f"📦 {row['name']} ({row['plans']})",

                callback_data=f"group_{row['name']}"

            )

        ])

    nav = []

    if page > 0:

        nav.append(

            InlineKeyboardButton(

                "⬅️ Prev",

                callback_data="product_prev"

            )

        )

    if offset + limit < total:

        nav.append(

            InlineKeyboardButton(

                "➡️ Next",

                callback_data="product_next"

            )

        )

    if nav:

        keyboard.append(nav)

    keyboard.append([

        InlineKeyboardButton(

            "➕ Add Product",

            callback_data="add_product"

        )

    ])

    keyboard.append([

        InlineKeyboardButton(

            "⬅️ Back",

            callback_data="products"

        ),

        InlineKeyboardButton(

            "🏠 Admin",

            callback_data="admin"

        )

    ])

    await edit(

        query,

f"""📦 PRODUCT LIST

━━━━━━━━━━━━━━

Products : {total}

Page : {page+1}

━━━━━━━━━━━━━━

Select a Product.
""",

        InlineKeyboardMarkup(

            keyboard

        )

    )

# ==========================
# PRODUCT PLANS
# ==========================

@route("group")
async def product_group(update: Update,
                        context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    uid = update.effective_user.id

    name = query.data.replace(
        "group_",
        ""
    )

    set(
        uid,
        "selected_product",
        name
    )

    cur.execute(
        """
        SELECT
            id,
            duration,
            price,
            status
        FROM products
        WHERE name=?
        ORDER BY id ASC
        """,
        (name,)
    )

    rows = cur.fetchall()

    keyboard = []

    if not rows:

        await query.answer(
            "❌ Product Not Found",
            show_alert=True
        )

        return

    for row in rows:

        icon = "🟢" if row["status"] == "on" else "🔴"

        keyboard.append([

            InlineKeyboardButton(

                f"{icon} {row['duration']} • {row['price']} Tk",

                callback_data=f"plan_{row['id']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "➕ Add Duration",
            callback_data="add_duration"
        )

    ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="product_list"
        ),

        InlineKeyboardButton(
            "🏠 Admin",
            callback_data="admin"
        )

    ])

    await edit(

        query,

f"""📦 {name}

━━━━━━━━━━━━━━

Available Plans

━━━━━━━━━━━━━━

Select a Duration.
""",

        InlineKeyboardMarkup(
            keyboard
        )

    )

# ==========================
# ADD DURATION
# ==========================

@route("add_duration")
async def add_duration(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    uid = update.effective_user.id

    await query.answer()

    start_input(
        uid,
        "add_product_duration"
    )

    set(
        uid,
        "new_product_name",
        value(uid,"selected_product")
    )

    msg = await query.edit_message_text(
        text=f"""📦 {value(uid,'selected_product')}

    ━━━━━━━━━━━━━━

    ⏳ Send Duration

    Example:

    30 Days
    365 Days
    Lifetime
    """,
        reply_markup=back_admin()
    )

    set(
        uid,
        "product_message",
        msg.message_id
    )

    set(
        uid,
        "new_product_name",
        value(uid,"selected_product")
    )

# ==========================
# PLAN DETAILS
# ==========================

@route("plan")
async def product_details(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    uid = update.effective_user.id

    pid = int(
        query.data.replace(
            "plan_",
            ""
        )
    )

    set(
        uid,
        "selected_plan",
        pid
    )

    cur.execute(
        """
        SELECT *
        FROM products
        WHERE id=?
        """,
        (pid,)
    )

    row = cur.fetchone()

    if not row:

        await query.answer(
            "❌ Plan Not Found",
            show_alert=True
        )

        return

    status = (
        "🟢 Enabled"
        if row["status"] == "on"
        else "🔴 Disabled"
    )

    await edit(

        query,

f"""📦 PRODUCT DETAILS

━━━━━━━━━━━━━━

📦 Name :
{row['name']}

⏳ Duration :
{row['duration']}

💰 Price :
{row['price']} Tk

📡 Status :
{status}
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "✏️ Edit Name",
                    callback_data="edit_name"
                )

            ],

            [

                InlineKeyboardButton(
                    "⏳ Edit Duration",
                    callback_data="edit_duration"
                ),

                InlineKeyboardButton(
                    "💰 Edit Price",
                    callback_data="edit_price"
                )

            ],

            [

                InlineKeyboardButton(
                    "🔄 ON / OFF",
                    callback_data="toggle_plan"
                )

            ],

            [

                InlineKeyboardButton(
                    "🗑 Delete",
                    callback_data="delete_plan"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data=f"group_{row['name']}"
                ),

                InlineKeyboardButton(
                    "🏠 Admin",
                    callback_data="admin"
                )

            ]

        ])

    )

# ==========================
# TOGGLE PLAN
# ==========================

@route("toggle_plan")
async def toggle_plan(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    pid = value(
        update.effective_user.id,
        "selected_plan"
    )

    cur.execute(
        """
        SELECT status
        FROM products
        WHERE id=?
        """,
        (pid,)
    )

    row = cur.fetchone()

    if not row:

        await query.answer(
            "❌ Plan Not Found",
            show_alert=True
        )

        return

    status = (
        "off"
        if row["status"] == "on"
        else "on"
    )

    cur.execute(
        """
        UPDATE products
        SET status=?
        WHERE id=?
        """,
        (
            status,
            pid
        )
    )

    db.commit()

    query.data = f"plan_{pid}"

    await product_details(
        update,
        context
    )

@route("delete_plan")
async def delete_plan(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await edit(

        query,

"""⚠️ DELETE PLAN

━━━━━━━━━━━━━━

Are you sure?

This action cannot be undone.
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "✅ Yes",
                    callback_data="delete_plan_yes"
                ),

                InlineKeyboardButton(
                    "❌ No",
                    callback_data="plan_back"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="plan_back"
                ),

                InlineKeyboardButton(
                    "🏠 Admin",
                    callback_data="admin"
                )

            ]

        ])

    )

@route("delete_plan_yes")
async def delete_plan_yes(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    uid = update.effective_user.id

    pid = value(
        uid,
        "selected_plan"
    )

    product = value(
        uid,
        "selected_product"
    )

    cur.execute(
        """
        DELETE
        FROM products
        WHERE id=?
        """,
        (pid,)
    )

    db.commit()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM products
        WHERE name=?
        """,
        (product,)
    )

    left = cur.fetchone()[0]

    if left == 0:

        await product_list(
            update,
            context
        )

        return

    query.data = f"group_{product}"

    await product_group(
        update,
        context
    )

@route("plan_back")
async def plan_back(update: Update,
                    context: ContextTypes.DEFAULT_TYPE):

    product = value(
        update.effective_user.id,
        "selected_product"
    )

    await render_product_details(
        update.callback_query,
        pid
    )

# ==========================
# ADD PRODUCT
# ==========================

@route("add_product")
async def add_product(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    start_input(
        update.effective_user.id,
        "add_product_name"
    )

    msg = await query.edit_message_text(

    """➕ ADD PRODUCT

    ━━━━━━━━━━━━━━

    Send Product Name

    Example:

    Netflix
    Spotify
    YouTube
    """,

    reply_markup=back_admin()

    )

    set(
        update.effective_user.id,
        "product_message",
        msg.message_id
    )

async def save_product_name(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    await delete_input(update)

    name = update.message.text.strip()

    if not name:

        return

    set(
        uid,
        "new_product_name",
        name
    )

    start_input(
        uid,
        "add_product_duration"
    )

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=value(
            uid,
            "product_message"
        ),

text=f"""📦 {name}

━━━━━━━━━━━━━━

Send Duration

Example

30 Days
365 Days
Lifetime
""",

        reply_markup=back_admin()

    )

async def save_product_duration(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    await delete_input(update)

    duration = update.message.text.strip()

    if not duration:

        return

    set(
        uid,
        "new_duration",
        duration
    )

    start_input(
        uid,
        "add_product_price"
    )

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=value(
            uid,
            "product_message"
        ),

text=f"""📦 {value(uid,'new_product_name')}

━━━━━━━━━━━━━━

⏳ {duration}

━━━━━━━━━━━━━━

Send Price
""",

        reply_markup=back_admin()

    )

# ==========================
# SAVE PRODUCT
# ==========================

async def save_product_price(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    await delete_input(update)

    try:

        price = int(
            update.message.text.strip()
        )

    except:

        return

    name = value(
        uid,
        "new_product_name"
    )

    duration = value(
        uid,
        "new_duration"
    )

    # Duplicate Duration Check

    cur.execute(

        """
        SELECT id

        FROM products

        WHERE

            name=?

        AND

            duration=?

        """,

        (

            name,

            duration

        )

    )

    if cur.fetchone():

        await context.bot.edit_message_text(

            chat_id=update.effective_chat.id,

            message_id=value(
                uid,
                "product_message"
            ),

            text=f"""❌ PLAN ALREADY EXISTS

━━━━━━━━━━━━━━

📦 {name}

⏳ {duration}

already exists.
""",

            reply_markup=back_admin()

        )

        stop_input(uid)

        return

    cur.execute(

        """
        INSERT INTO products(

            name,

            duration,

            price,

            status

        )

        VALUES(

            ?, ?, ?, ?

        )

        """,

        (

            name,

            duration,

            price,

            "on"

        )

    )

    db.commit()

    stop_input(uid)


    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=value(
            uid,
            "product_message"
        ),

        text=f"""✅ PRODUCT SAVED

━━━━━━━━━━━━━━

📦 {name}

⏳ {duration}

💰 {price} Tk

🟢 Status : ON
""",

        reply_markup=success_keyboard()

    )


# ==========================
# EDIT PRODUCT
# ==========================

@route("edit_name")
async def edit_name(update: Update,
                    context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    start_input(
        update.effective_user.id,
        "edit_name"
    )

    await edit(

        query,

"""✏️ EDIT PRODUCT NAME

━━━━━━━━━━━━━━

Send New Product Name
""",

        back_admin()

    )


async def save_edit_name(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    await delete_input(update)

    name = update.message.text.strip()

    pid = value(
        uid,
        "selected_plan"
    )

    cur.execute(

        """
        UPDATE products
        SET name=?
        WHERE id=?
        """,

        (
            name,
            pid
        )

    )

    db.commit()

    stop_input(uid)

    cur.execute(
        "SELECT * FROM products WHERE id=?",
        (pid,)
    )

    row = cur.fetchone()

    update.message = None

    class Dummy:
        pass

    query = Dummy()

    query.data = f"plan_{pid}"

    query.message = None

    update.callback_query = query

    await product_details(
        update,
        context
    )

@route("edit_duration")
async def edit_duration(update: Update,
                        context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    start_input(
        update.effective_user.id,
        "edit_duration"
    )

    await edit(

        query,

"""⏳ EDIT DURATION

━━━━━━━━━━━━━━

Send New Duration
""",

        back_admin()

    )


async def save_edit_duration(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    await delete_input(update)

    duration = update.message.text.strip()

    pid = value(
        uid,
        "selected_plan"
    )

    cur.execute(

        """
        UPDATE products
        SET duration=?
        WHERE id=?
        """,

        (
            duration,
            pid
        )

    )

    db.commit()

    stop_input(uid)

    await render_product_details(
        update.callback_query,
        pid
    )

@route("edit_price")
async def edit_price(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    start_input(
        update.effective_user.id,
        "edit_price"
    )

    await edit(

        query,

"""💰 EDIT PRICE

━━━━━━━━━━━━━━

Send New Price
""",

        back_admin()

    )


async def save_edit_price(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    await delete_input(update)

    try:

        price = int(update.message.text)

    except:

        return

    pid = value(
        uid,
        "selected_plan"
    )

    cur.execute(

        """
        UPDATE products
        SET price=?
        WHERE id=?
        """,

        (
            price,
            pid
        )

    )

    db.commit()

    stop_input(uid)

    await render_product_details(
        update.callback_query,
        pid
    )


# ==========================
# SEARCH PRODUCT
# ==========================

@route("search_product")
async def search_product(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    start_input(
        update.effective_user.id,
        "search_product"
    )

    await edit(

        query,

"""🔍 SEARCH PRODUCT

━━━━━━━━━━━━━━

Send Product Name
""",

        back_admin()

    )


async def search_product_input(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    await delete_input(update)

    keyword = update.message.text.strip()

    stop_input(uid)

    cur.execute(

        """
        SELECT

            name,

            COUNT(*) plans

        FROM products

        WHERE

            name LIKE ?

        GROUP BY name

        ORDER BY name

        """,

        (f"%{keyword}%",)

    )

    rows = cur.fetchall()

    keyboard = []

    if rows:

        for row in rows:

            keyboard.append([

                InlineKeyboardButton(

                    f"📦 {row['name']} ({row['plans']})",

                    callback_data=f"group_{row['name']}"

                )

            ])

    else:

        keyboard.append([

            InlineKeyboardButton(

                "❌ No Product Found",

                callback_data="products"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(

            "⬅️ Back",

            callback_data="products"

        ),

        InlineKeyboardButton(

            "🏠 Admin",

            callback_data="admin"

        )

    ])

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=value(uid, "product_message"),

        text="🔍 SEARCH RESULT",

        reply_markup=InlineKeyboardMarkup(keyboard)

    )

@route("product_prev")
async def product_prev(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    page = value(uid, "product_page") or 0

    if page > 0:

        set(uid, "product_page", page - 1)

    await product_list(update, context)


@route("product_next")
async def product_next(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    page = value(uid, "product_page") or 0

    set(uid, "product_page", page + 1)

    await product_list(update, context)

# ==========================
# RENDER DETAILS
# ==========================

async def render_product_details(
    query,
    pid
):

    cur.execute(
        """
        SELECT *
        FROM products
        WHERE id=?
        """,
        (pid,)
    )

    row = cur.fetchone()

    if not row:

        await query.answer(
            "❌ Product Not Found",
            show_alert=True
        )

        return

    status = "🟢 ON"

    if row["status"] == "off":

        status = "🔴 OFF"

    await edit(

        query,

f"""📦 PRODUCT DETAILS

━━━━━━━━━━━━━━

📦 Name :
{row['name']}

━━━━━━━━━━━━━━

⏳ Duration :
{row['duration']}

━━━━━━━━━━━━━━

💰 Price :
{row['price']} Tk

━━━━━━━━━━━━━━

📡 Status :
{status}
""",

        details_keyboard()

    )

async def render_product_group(

    query,

    name

):

    cur.execute(

        """
        SELECT

            id,

            duration,

            price,

            status

        FROM products

        WHERE name=?

        ORDER BY id

        """,

        (name,)

    )

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        icon = "🟢"

        if row["status"] == "off":

            icon = "🔴"

        keyboard.append([

            InlineKeyboardButton(

                f"{icon} {row['duration']} • {row['price']} Tk",

                callback_data=f"plan_{row['id']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(

            "➕ Add Duration",

            callback_data="add_duration"

        )

    ])

    keyboard.append([

        InlineKeyboardButton(

            "⬅️ Back",

            callback_data="product_list"

        ),

        InlineKeyboardButton(

            "🏠 Admin",

            callback_data="admin"

        )

    ])

    await edit(

        query,

f"""📦 {name}

━━━━━━━━━━━━━━

Available Plans
""",

        InlineKeyboardMarkup(

            keyboard

        )

    )

# ==========================
# SESSION
# ==========================

def clear_product_session(uid):

    keys = [

        "selected_product",

        "selected_plan",

        "new_product_name",

        "new_duration",

        "product_page",

        "search_keyword",

        "edit_mode"

    ]

    for key in keys:

        try:

            clear(uid, key)

        except:

            pass
@route("cancel_product")

async def cancel_product(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    stop_input(uid)

    clear_product_session(uid)

    await products(
        update,
        context
    )

async def refresh_products(update,
                           context):

    uid = update.effective_user.id

    stop_input(uid)

    clear_product_session(uid)

    await product_list(
        update,
        context
    )

async def no_product(query):

    await edit(

        query,

"""📦 PRODUCTS

━━━━━━━━━━━━━━

No Product Available.
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(

                    "➕ Add Product",

                    callback_data="add_product"

                )

            ],

            [

                InlineKeyboardButton(

                    "⬅️ Back",

                    callback_data="products"

                ),

                InlineKeyboardButton(

                    "🏠 Admin",

                    callback_data="admin"

                )

            ]

        ])

    )

async def no_duration(query,
                      name):

    await edit(

        query,

f"""📦 {name}

━━━━━━━━━━━━━━

No Duration Found.
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(

                    "➕ Add Duration",

                    callback_data="add_duration"

                )

            ],

            [

                InlineKeyboardButton(

                    "⬅️ Back",

                    callback_data="product_list"

                ),

                InlineKeyboardButton(

                    "🏠 Admin",

                    callback_data="admin"

                )

            ]

        ])

    )



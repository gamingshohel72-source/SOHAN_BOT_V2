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

from input import (
    start_input,
    stop_input
)

from payments.session import (
    set,
    value
)

from datetime import datetime
from datetime import datetime, timedelta

import secrets
import string

alphabet = string.ascii_uppercase + string.digits


def generate_key(prefix, groups, length):

    parts = []

    for _ in range(groups):

        parts.append(

            "".join(

                secrets.choice(alphabet)

                for _ in range(length)

            )

        )

    return prefix + "-" + "-".join(parts)


def generate_order_no():

    cur.execute(
        "SELECT COUNT(*) FROM orders"
    )

    total = cur.fetchone()[0] + 1

    return f"GH{100000 + total}"


def add_key_log(
    admin_id,
    product_id,
    product_name,
    duration,
    action,
    quantity,
    details=""
):

    cur.execute(

        """
        INSERT INTO key_logs(

            admin_id,
            product_id,
            product_name,
            duration,
            action,
            quantity,
            details,
            created_at

        )

        VALUES(?,?,?,?,?,?,?,?)

        """,

        (

            admin_id,
            product_id,
            product_name,
            duration,
            action,
            quantity,
            details,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        )

    )

    db.commit()


@route("keys")
async def keys(update: Update,
               context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("SELECT COUNT(*) FROM keys")
    total = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM keys WHERE status='unused'"
    )
    available = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM keys WHERE status='used'"
    )
    used = cur.fetchone()[0]

    duplicate = total - cur.execute(
        """
        SELECT COUNT(DISTINCT key)
        FROM keys
        """
    ).fetchone()[0]

    text = f"""🔑 KEY MANAGER

━━━━━━━━━━━━━━

🔑 Total Keys : {total}

🟢 Available : {available}

🔴 Used : {used}

🧹 Duplicate : {duplicate}

━━━━━━━━━━━━━━

Select an option.
"""

    await edit(

        query,

        text,

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "➕ Add Keys",
                    callback_data="add_keys"
                ),

                InlineKeyboardButton(
                    "⚡ Generate",
                    callback_data="generate_keys"
                )

            ],

            [

                InlineKeyboardButton(
                    "📥 Import TXT",
                    callback_data="import_keys"
                ),

                InlineKeyboardButton(
                    "📤 Export TXT",
                    callback_data="export_keys"
                )

            ],

            [

                InlineKeyboardButton(
                    "📋 View",
                    callback_data="view_keys"
                ),

                InlineKeyboardButton(
                    "🔍 Search",
                    callback_data="search_key"
                )

            ],

            [
                InlineKeyboardButton(
                    "⚙️ Auto Delete",
                    callback_data="auto_delete_panel"
                )

            ],

            [

                InlineKeyboardButton(
                    "📊 Statistics",
                    callback_data="key_statistics"
                ),

                InlineKeyboardButton(
                    "📜 History",
                    callback_data="key_history"
                )

            ],

            [

                InlineKeyboardButton(
                    "🗑 Delete",
                    callback_data="delete_keys"
                ),

                InlineKeyboardButton(
                    "🧹 Duplicate",
                    callback_data="duplicate_keys"
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


@route("add_keys")
async def add_keys(update: Update,
                   context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT DISTINCT name
        FROM products
        WHERE status='on'
        ORDER BY name
    """)

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(
                row["name"],
                callback_data=f"key_product_{row['name']}"
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="keys"
        )

    ])

    await edit(

        query,

"""➕ ADD KEYS

━━━━━━━━━━━━━━

Select Product
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("key_product")
async def key_product(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    product = query.data.replace(
        "key_product_",
        ""
    )

    set(
        update.effective_user.id,
        "key_product",
        product
    )

    cur.execute("""
        SELECT
            id,
            duration,
            price
        FROM products
        WHERE name=?
        ORDER BY id
    """, (product,))

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(

                f"{row['duration']} • {row['price']} Tk",

                callback_data=f"key_duration_{row['id']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="add_keys"
        )

    ])

    await edit(

        query,

        f"""📦 {product}

━━━━━━━━━━━━━━

Select Duration
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("key_duration")
async def key_duration(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    pid = int(
        query.data.replace(
            "key_duration_",
            ""
        )
    )

    cur.execute("""
        SELECT
            name,
            duration
        FROM products
        WHERE id=?
        LIMIT 1
    """, (pid,))

    row = cur.fetchone()

    if not row:

        await edit(
            query,
            "❌ Product Not Found"
        )

        return

    set(
        update.effective_user.id,
        "key_product",
        row["name"]
    )

    set(
        update.effective_user.id,
        "key_duration",
        row["duration"]
    )

    start_input(
        update.effective_user.id,
        "save_keys"
    )

    await edit(

        query,

f"""🔑 SEND KEYS

━━━━━━━━━━━━━━

📦 Product :
{row['name']}

⏳ Duration :
{row['duration']}

━━━━━━━━━━━━━━

Send one key per line.

Example

AAAA-BBBB-CCCC

DDDD-EEEE-FFFF
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="keys"
                )

            ]

        ])

    )


@route("generate_keys")
async def generate_keys(update: Update,
                        context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    set(
        update.effective_user.id,
        "generate_msg",
        query.message.message_id
    )

    cur.execute("""
        SELECT DISTINCT name
        FROM products
        WHERE status='on'
        ORDER BY name
    """)

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(
                row["name"],
                callback_data=f"gen_product_{row['name']}"
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="keys"
        )

    ])

    await edit(

        query,

"""⚡ GENERATE KEYS

━━━━━━━━━━━━━━

Select Product
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("gen_product")
async def gen_product(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    product = query.data.replace(
        "gen_product_",
        ""
    )

    set(
        update.effective_user.id,
        "gen_product",
        product
    )

    cur.execute("""
        SELECT
            id,
            duration,
            price
        FROM products
        WHERE name=?
        ORDER BY id
    """, (product,))

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(

                f"{row['duration']} • {row['price']} Tk",

                callback_data=f"gen_duration_{row['id']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="generate_keys"
        )

    ])

    await edit(

        query,

        f"""📦 {product}

━━━━━━━━━━━━━━

Select Duration
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("gen_duration")
async def gen_duration(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    pid = int(
        query.data.replace(
            "gen_duration_",
            ""
        )
    )

    cur.execute("""
        SELECT
            name,
            duration
        FROM products
        WHERE id=?
        LIMIT 1
    """, (pid,))

    row = cur.fetchone()

    if not row:

        await edit(
            query,
            "❌ Product Not Found"
        )

        return

    set(
        update.effective_user.id,
        "gen_product",
        row["name"]
    )

    set(
        update.effective_user.id,
        "gen_duration",
        row["duration"]
    )

    keyboard = []

    for start in range(1, 21, 5):

        buttons = []

        for i in range(start, min(start + 5, 21)):

            buttons.append(
                InlineKeyboardButton(
                    str(i),
                    callback_data=f"group_count_{i}"
                )
            )

        keyboard.append(buttons)

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="generate_keys"
        )
    ])

    await edit(

        query,

"""🔢 SELECT GROUP COUNT

━━━━━━━━━━━━━━

Select Group Count
""",

        InlineKeyboardMarkup(
            keyboard
        )

    )

@route("group_count")
async def group_count(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    group = int(
        query.data.replace(
            "group_count_",
            ""
        )
    )

    set(
        update.effective_user.id,
        "gen_group",
        group
    )

    keyboard = []

    for start in range(1, 21, 5):

        buttons = []

        for i in range(start, min(start + 5, 21)):

            buttons.append(
                InlineKeyboardButton(
                    str(i),
                    callback_data=f"key_length_{i}"
                )
            )

        keyboard.append(buttons)

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="generate_keys"
        )

    ])

    await edit(

        query,

f"""📏 SELECT GROUP LENGTH

━━━━━━━━━━━━━━

🔢 Groups : {group}

Select Length For Each Group
""",

        InlineKeyboardMarkup(
            keyboard
        )

    )


@route("key_length")
async def key_length(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    length = int(
        query.data.replace(
            "key_length_",
            ""
        )
    )

    set(
        update.effective_user.id,
        "gen_length",
        length
    )

    group = value(
        update.effective_user.id,
        "gen_group"
    )

    start_input(
        update.effective_user.id,
        "generate_count"
    )

    await edit(

        query,

f"""⚡ GENERATE KEYS

━━━━━━━━━━━━━━

🔢 Groups : {group}

📏 Group Length : {length}

━━━━━━━━━━━━━━

Send Generate Count

Example

100
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="generate_keys"
                )

            ]

        ])

    )


@route("import_keys")
async def import_keys(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT DISTINCT name
        FROM products
        WHERE status='on'
        ORDER BY name
    """)

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(
                row["name"],
                callback_data=f"import_product_{row['name']}"
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="keys"
        )

    ])

    await edit(

        query,

"""📥 IMPORT KEYS

━━━━━━━━━━━━━━

Select Product
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("import_product")
async def import_product(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    product = query.data.replace(
        "import_product_",
        ""
    )

    set(
        update.effective_user.id,
        "import_product",
        product
    )

    cur.execute("""
        SELECT
            id,
            duration,
            price
        FROM products
        WHERE name=?
        ORDER BY id
    """, (product,))

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(

                f"{row['duration']} • {row['price']} Tk",

                callback_data=f"import_duration_{row['id']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="import_keys"
        )

    ])

    await edit(

        query,

        f"""📦 {product}

━━━━━━━━━━━━━━

Select Duration
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("import_duration")
async def import_duration(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    pid = int(
        query.data.replace(
            "import_duration_",
            ""
        )
    )

    cur.execute("""
        SELECT
            name,
            duration
        FROM products
        WHERE id=?
        LIMIT 1
    """, (pid,))

    row = cur.fetchone()

    if not row:

        await edit(
            query,
            "❌ Product Not Found"
        )

        return

    set(
        update.effective_user.id,
        "import_product",
        row["name"]
    )

    set(
        update.effective_user.id,
        "import_duration",
        row["duration"]
    )

    start_input(
        update.effective_user.id,
        "import_txt"
    )

    await edit(

        query,

f"""📥 IMPORT TXT

━━━━━━━━━━━━━━

📦 Product :
{row['name']}

⏳ Duration :
{row['duration']}

━━━━━━━━━━━━━━

Send TXT File

• Only .txt

• One key per line
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="keys"
                )

            ]

        ])

    )


@route("export_keys")
async def export_keys(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await edit(

        query,

"""📤 EXPORT KEYS

━━━━━━━━━━━━━━

Choose Export Type
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🟢 Available",
                    callback_data="export_available"
                ),

                InlineKeyboardButton(
                    "🔴 Used",
                    callback_data="export_used"
                )

            ],

            [

                InlineKeyboardButton(
                    "📦 All Keys",
                    callback_data="export_all"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="keys"
                )

            ]

        ])

    )


async def export_product_menu(
    query,
    export_type
):

    cur.execute("""
        SELECT DISTINCT name
        FROM products
        WHERE status='on'
        ORDER BY name
    """)

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(

                row["name"],

                callback_data=(
                    f"export_product_"
                    f"{export_type}_"
                    f"{row['name']}"
                )

            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="export_keys"
        )

    ])

    await edit(

        query,

f"""📤 EXPORT

━━━━━━━━━━━━━━

Type : {export_type.upper()}

━━━━━━━━━━━━━━

Select Product
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("export_available")
async def export_available(update, context):

    await export_product_menu(
        update.callback_query,
        "available"
    )


@route("export_used")
async def export_used(update, context):

    await export_product_menu(
        update.callback_query,
        "used"
    )


@route("export_all")
async def export_all(update, context):

    await export_product_menu(
        update.callback_query,
        "all"
    )


@route("export_product")
async def export_product(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    data = query.data.split("_", 3)

    export_type = data[2]

    product = data[3]

    set(
        update.effective_user.id,
        "export_type",
        export_type
    )

    set(
        update.effective_user.id,
        "export_product",
        product
    )

    cur.execute("""

        SELECT
            id,
            duration

        FROM products

        WHERE name=?

        ORDER BY id

    """, (product,))

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(

                row["duration"],

                callback_data=f"export_duration_{row['id']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data=f"export_{export_type}"
        )

    ])

    await edit(

        query,

f"""📦 {product}

━━━━━━━━━━━━━━

Select Duration
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("export_duration")
async def export_duration(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    pid = int(
        query.data.replace(
            "export_duration_",
            ""
        )
    )

    cur.execute("""

        SELECT
            name,
            duration

        FROM products

        WHERE id=?

        LIMIT 1

    """, (pid,))

    row = cur.fetchone()

    if not row:

        await edit(
            query,
            "❌ Product Not Found"
        )

        return

    set(
        update.effective_user.id,
        "export_product",
        row["name"]
    )

    set(
        update.effective_user.id,
        "export_duration",
        row["duration"]
    )

    start_input(
        update.effective_user.id,
        "export_keys_txt"
    )

    await edit(

        query,

f"""📤 EXPORT READY

━━━━━━━━━━━━━━

📦 Product :
{row['name']}

⏳ Duration :
{row['duration']}

━━━━━━━━━━━━━━

Press Continue
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "📤 Export",
                    callback_data="export_now"
                )

            ],

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="keys"
                )

            ]

        ])

    )


@route("view_keys")
async def view_keys(update: Update,
                    context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT DISTINCT name
        FROM products
        WHERE status='on'
        ORDER BY name
    """)

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(
                row["name"],
                callback_data=f"view_key_product_{row['name']}"
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="keys"
        )

    ])

    await edit(

        query,

"""📋 VIEW KEYS

━━━━━━━━━━━━━━

Select Product
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("view_key_product")
async def view_key_product(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    product = query.data.replace(
        "view_key_product_",
        ""
    )

    cur.execute("""

        SELECT
            id,
            duration,
            price

        FROM products

        WHERE name=?

        ORDER BY id

    """, (product,))

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(

                f"{row['duration']} • {row['price']} Tk",

                callback_data=f"view_key_duration_{row['id']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="view_keys"
        )

    ])

    await edit(

        query,

f"""📦 {product}

━━━━━━━━━━━━━━

Select Duration
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("view_key_duration")
async def view_key_duration(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    pid = int(
        query.data.replace(
            "view_key_duration_",
            ""
        )
    )

    cur.execute("""

        SELECT
            id,
            name,
            duration

        FROM products

        WHERE id=?

        LIMIT 1

    """, (pid,))

    product = cur.fetchone()

    if not product:

        await edit(
            query,
            "❌ Product Not Found"
        )

        return

    cur.execute("""

        SELECT COUNT(*)

        FROM keys

        WHERE product=?
        AND duration=?

    """, (

        product["name"],
        product["duration"]

    ))

    total = cur.fetchone()[0]

    cur.execute("""

        SELECT COUNT(*)

        FROM keys

        WHERE product=?
        AND duration=?
        AND status='unused'

    """, (

        product["name"],
        product["duration"]

    ))

    available = cur.fetchone()[0]

    used = total - available

    await edit(

        query,

f"""🔑 KEY INFORMATION

━━━━━━━━━━━━━━

📦 Product :
{product['name']}

⏳ Duration :
{product['duration']}

━━━━━━━━━━━━━━

📦 Total :
{total}

🟢 Available :
{available}

🔴 Used :
{used}
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🟢 Available",
                    callback_data=f"available_keys_{pid}"
                ),

                InlineKeyboardButton(
                    "🔴 Used",
                    callback_data=f"used_keys_{pid}"
                )

            ],

            [

                InlineKeyboardButton(
                    "📤 Export",
                    callback_data=f"export_product_all_{product['name']}"
                ),

                InlineKeyboardButton(
                    "🗑 Delete",
                    callback_data=f"delete_product_keys_{pid}"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data=f"view_key_product_{product['name']}"
                )

            ]

        ])

    )


@route("available_keys")
async def available_keys(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    data = query.data.split("_")

    pid = int(data[2])

    page = int(data[3]) if len(data) > 3 else 1

    per_page = 20

    cur.execute("""
        SELECT
            name,
            duration
        FROM products
        WHERE id=?
    """, (pid,))

    product = cur.fetchone()

    if not product:

        await edit(
            query,
            "❌ Product Not Found"
        )

        return

    cur.execute("""
        SELECT COUNT(*)
        FROM keys
        WHERE product=?
        AND duration=?
        AND status='unused'
    """, (
        product["name"],
        product["duration"]
    ))

    total = cur.fetchone()[0]

    pages = max(
        1,
        (total + per_page - 1) // per_page
    )

    offset = (page - 1) * per_page

    cur.execute("""
        SELECT
            id,
            key,
            created_at
        FROM keys
        WHERE product=?
        AND duration=?
        AND status='unused'
        ORDER BY id
        LIMIT ?
        OFFSET ?
    """, (
        product["name"],
        product["duration"],
        per_page,
        offset
    ))

    rows = cur.fetchall()

    text = f"""🟢 AVAILABLE KEYS

━━━━━━━━━━━━━━

📦 {product['name']}

⏳ {product['duration']}

📄 Page {page}/{pages}

━━━━━━━━━━━━━━

"""

    if not rows:

        text += "No Available Keys."

    else:

        for row in rows:

            text += (

                f"🔑 {row['key']}\n"

                f"🕒 {row['created_at']}\n\n"

            )

    keyboard = []

    nav = []

    if page > 1:

        nav.append(

            InlineKeyboardButton(
                "⬅️ Prev",
                callback_data=f"available_keys_{pid}_{page-1}"
            )

        )

    if page < pages:

        nav.append(

            InlineKeyboardButton(
                "Next ➡️",
                callback_data=f"available_keys_{pid}_{page+1}"
            )

        )

    if nav:

        keyboard.append(nav)

    keyboard.append([

        InlineKeyboardButton(
            "📋 Copy All",
            callback_data=f"copy_available_{pid}"
        )

    ])

    keyboard.append([

        InlineKeyboardButton(
            "📤 Export",
            callback_data=f"export_product_all_{product['name']}"
        ),

        InlineKeyboardButton(
            "🗑 Delete",
            callback_data=f"delete_product_keys_{pid}"
        )

    ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data=f"view_key_duration_{pid}"
        )

    ])

    await edit(

        query,

        text,

        InlineKeyboardMarkup(keyboard)

    )


@route("used_keys")
async def used_keys(update: Update,
                    context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    data = query.data.split("_")

    pid = int(data[2])

    page = int(data[3]) if len(data) > 3 else 1

    per_page = 20

    cur.execute("""
        SELECT
            name,
            duration
        FROM products
        WHERE id=?
    """, (pid,))

    product = cur.fetchone()

    if not product:

        await edit(
            query,
            "❌ Product Not Found"
        )

        return

    cur.execute("""
        SELECT COUNT(*)
        FROM keys
        WHERE product=?
        AND duration=?
        AND status='used'
    """, (
        product["name"],
        product["duration"]
    ))

    total = cur.fetchone()[0]

    pages = max(
        1,
        (total + per_page - 1) // per_page
    )

    offset = (page - 1) * per_page

    cur.execute("""
        SELECT
            id,
            key,
            buyer_id,
            order_id,
            used_at
        FROM keys
        WHERE product=?
        AND duration=?
        AND status='used'
        ORDER BY used_at DESC
        LIMIT ?
        OFFSET ?
    """, (
        product["name"],
        product["duration"],
        per_page,
        offset
    ))

    rows = cur.fetchall()

    text = f"""🔴 USED KEYS

━━━━━━━━━━━━━━

📦 {product['name']}

⏳ {product['duration']}

📄 Page {page}/{pages}

━━━━━━━━━━━━━━

"""

    if not rows:

        text += "No Used Keys."

    else:

        for row in rows:

            text += (

                f"🔑 {row['key']}\n"

                f"👤 Buyer : {row['buyer_id'] or '-'}\n"

                f"🛒 Order : {row['order_id'] or '-'}\n"

                f"🕒 Used : {row['used_at'] or '-'}\n\n"

            )

    keyboard = []

    nav = []

    if page > 1:

        nav.append(

            InlineKeyboardButton(
                "⬅️ Prev",
                callback_data=f"used_keys_{pid}_{page-1}"
            )

        )

    if page < pages:

        nav.append(

            InlineKeyboardButton(
                "Next ➡️",
                callback_data=f"used_keys_{pid}_{page+1}"
            )

        )

    if nav:

        keyboard.append(nav)

    keyboard.append([

        InlineKeyboardButton(
            "🔄 Replace Key",
            callback_data=f"replace_key_{pid}"
        )

    ])

    keyboard.append([

        InlineKeyboardButton(
            "📤 Export Used",
            callback_data=f"export_product_used_{product['name']}"
        )

    ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data=f"view_key_duration_{pid}"
        )

    ])

    await edit(

        query,

        text,

        InlineKeyboardMarkup(keyboard)

    )

@route("key_statistics")
async def key_statistics(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("SELECT COUNT(*) FROM keys")
    total = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM keys WHERE status='unused'"
    )
    available = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM keys WHERE status='used'"
    )
    used = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(DISTINCT product)
        FROM keys
    """)
    products = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM keys
        GROUP BY product,duration
        HAVING COUNT(*)<=10
    """)

    low_stock = len(cur.fetchall())

    duplicate = total - cur.execute(
        """
        SELECT COUNT(DISTINCT key)
        FROM keys
        """
    ).fetchone()[0]

    text = f"""📊 KEY STATISTICS

━━━━━━━━━━━━━━

🔑 Total Keys :
{total}

🟢 Available :
{available}

🔴 Used :
{used}

🧹 Duplicate :
{duplicate}

📦 Products :
{products}

⚠️ Low Stock :
{low_stock}

━━━━━━━━━━━━━━
"""

    await edit(

        query,

        text,

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🔄 Refresh",
                    callback_data="key_statistics"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="keys"
                )

            ]

        ])

    )

@route("search_key")
async def search_key(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await edit(

        query,

"""🔍 SEARCH KEY

━━━━━━━━━━━━━━

Choose Search Type
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🔑 Search Key",
                    callback_data="search_by_key"
                )

            ],

            [

                InlineKeyboardButton(
                    "👤 Buyer ID",
                    callback_data="search_by_buyer"
                ),

                InlineKeyboardButton(
                    "🛒 Order ID",
                    callback_data="search_by_order"
                )

            ],

            [

                InlineKeyboardButton(
                    "📦 Product",
                    callback_data="search_by_product"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="keys"
                )

            ]

        ])

    )


@route("search_by_key")
async def search_by_key(update: Update,
                        context: ContextTypes.DEFAULT_TYPE):

    start_input(
        update.effective_user.id,
        "search_key_value"
    )

    await edit(

        update.callback_query,

"""🔑 SEARCH KEY

━━━━━━━━━━━━━━

Send Full Key
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="search_key"
                )

            ]

        ])

    )


@route("search_by_buyer")
async def search_by_buyer(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):

    start_input(
        update.effective_user.id,
        "search_buyer_value"
    )

    await edit(

        update.callback_query,

"""👤 SEARCH BUYER

━━━━━━━━━━━━━━

Send Buyer ID
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="search_key"
                )

            ]

        ])

    )


@route("search_by_order")
async def search_by_order(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):

    start_input(
        update.effective_user.id,
        "search_order_value"
    )

    await edit(

        update.callback_query,

"""🛒 SEARCH ORDER

━━━━━━━━━━━━━━

Send Order ID
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="search_key"
                )

            ]

        ])

    )


@route("search_by_product")
async def search_by_product(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):

    cur.execute("""

        SELECT DISTINCT name

        FROM products

        WHERE status='on'

        ORDER BY name

    """)

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(

                row["name"],

                callback_data=f"search_product_{row['name']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(

            "⬅️ Back",

            callback_data="search_key"

        )

    ])

    await edit(

        update.callback_query,

"""📦 SEARCH PRODUCT

━━━━━━━━━━━━━━

Select Product
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("search_product")
async def search_product(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    product = query.data.replace(
        "search_product_",
        ""
    )

    start_input(
        update.effective_user.id,
        "search_product_duration"
    )

    set(
        update.effective_user.id,
        "search_product",
        product
    )

    await edit(

        query,

f"""📦 {product}

━━━━━━━━━━━━━━

Send Duration

Example

30 Days
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="search_key"
                )

            ]

        ])

    )

@route("delete_keys")
async def delete_keys(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    await edit(

        update.callback_query,

"""🗑 DELETE KEYS

━━━━━━━━━━━━━━

Select Delete Option
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🟢 Available",
                    callback_data="delete_available_keys"
                ),

                InlineKeyboardButton(
                    "🔴 Used",
                    callback_data="delete_used_keys"
                )

            ],

            [

                InlineKeyboardButton(
                    "📦 Product",
                    callback_data="delete_product_menu"
                )

            ],

            [

                InlineKeyboardButton(
                    "🧹 Duplicate",
                    callback_data="delete_duplicate_keys"
                )

            ],

            [

                InlineKeyboardButton(
                    "💥 Delete All",
                    callback_data="delete_all_keys"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="keys"
                )

            ]

        ])

    )


@route("duplicate_keys")
async def duplicate_keys(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    cur.execute("""
        SELECT key,COUNT(*)
        FROM keys
        GROUP BY key
        HAVING COUNT(*)>1
    """)

    rows = cur.fetchall()

    text = f"""🧹 DUPLICATE KEYS

━━━━━━━━━━━━━━

Duplicate Found : {len(rows)}

━━━━━━━━━━━━━━
"""

    await edit(

        update.callback_query,

        text,

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🗑 Remove Duplicate",
                    callback_data="delete_duplicate_keys"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="keys"
                )

            ]

        ])

    )


@route("key_history")
async def key_history(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    cur.execute("""

        SELECT *

        FROM key_logs

        ORDER BY id DESC

        LIMIT 30

    """)

    rows = cur.fetchall()

    text = "📜 KEY HISTORY\n\n"

    if not rows:

        text += "No History."

    else:

        for row in rows:

            text += (

                f"👤 {row['admin_id']}\n"

                f"⚡ {row['action']}\n"

                f"📦 {row['product_name']}\n"

                f"⏳ {row['duration']}\n"

                f"🔑 {row['quantity']}\n"

                f"🕒 {row['created_at']}\n\n"

            )

    await edit(

        update.callback_query,

        text,

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🗑 Clear",
                    callback_data="clear_key_history"
                ),

                InlineKeyboardButton(
                    "🔄 Refresh",
                    callback_data="key_history"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="keys"
                )

            ]

        ])

    )


@route("clear_key_history")
async def clear_key_history(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):

    await edit(

        update.callback_query,

"""⚠️ CLEAR HISTORY

━━━━━━━━━━━━━━

Are you sure?

This cannot be undone.
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "✅ Yes",
                    callback_data="confirm_clear_key_history"
                )

            ],

            [

                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="key_history"
                )

            ]

        ])

    )


@route("confirm_clear_key_history")
async def confirm_clear_key_history(update: Update,
                                    context: ContextTypes.DEFAULT_TYPE):

    cur.execute("DELETE FROM key_logs")

    db.commit()

    await edit(

        update.callback_query,

"""✅ HISTORY CLEARED""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="keys"
                )

            ]

        ])

    )


async def save_keys(update: Update,
                    context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    product = value(uid, "key_product")

    duration = value(uid, "key_duration")

    lines = update.message.text.splitlines()

    added = 0

    duplicate = 0

    cur.execute(
        """
        SELECT id
        FROM products
        WHERE name=?
        AND duration=?
        LIMIT 1
        """,
        (
            product,
            duration
        )
    )

    row = cur.fetchone()

    product_id = row["id"] if row else None

    for line in lines:

        key = line.strip()

        if not key:
            continue

        cur.execute(
            "SELECT 1 FROM keys WHERE key=?",
            (key,)
        )

        if cur.fetchone():

            duplicate += 1

            continue

        cur.execute(
            """
            INSERT INTO keys(

                product,

                duration,

                key,

                status,

                created_at

            )

            VALUES(?,?,?,?,?)

            """,
            (

                product,

                duration,

                key,

                "unused",

                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            )

        )

        added += 1

    db.commit()

    add_key_log(

        admin_id=uid,

        product_id=product_id,

        product_name=product,

        duration=duration,

        action="ADD",

        quantity=added,

        details=f"Duplicate: {duplicate}"

    )

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    await update.message.reply_text(

    f"""✅ KEYS ADDED

    ━━━━━━━━━━━━━━

    📦 Product :
    {product}

    ⏳ Duration :
    {duration}

    ━━━━━━━━━━━━━━

    ✅ Added :
    {added}

    ⚠️ Duplicate :
    {duplicate}
    """,

        reply_markup=InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🔑 Keys",
                    callback_data="keys"
                ),

                InlineKeyboardButton(
                    "👑 Admin Panel",
                    callback_data="admin"
                )

            ]

        ])
    )

async def save_generate_count(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    try:

        count = int(update.message.text)

    except ValueError:

        await update.message.reply_text(
            "❌ Please enter a valid number."
        )

        return

    product = value(uid, "gen_product")

    duration = value(uid, "gen_duration")

    group = int(value(uid, "gen_group"))

    length = int(value(uid, "gen_length"))

    cur.execute(
        """
        SELECT
            id,
            prefix
        FROM products
        WHERE name=?
        AND duration=?
        LIMIT 1
        """,
        (
            product,
            duration
        )
    )

    row = cur.fetchone()

    if not row:

        await update.message.reply_text(
            "❌ Product Not Found."
        )

        stop_input(uid)

        return

    product_id = row["id"]

    prefix = row["prefix"]

    added = 0

    duplicate = 0

    while added < count:

        key = generate_key(
            prefix,
            group,
            length
        )

        cur.execute(
            "SELECT 1 FROM keys WHERE key=?",
            (key,)
        )

        if cur.fetchone():

            duplicate += 1

            continue

        cur.execute(
            """
            INSERT INTO keys(

                product,

                duration,

                key,

                status,

                created_at

            )

            VALUES(?,?,?,?,?)

            """,
            (
                product,
                duration,
                key,
                "unused",
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        )

        added += 1

    db.commit()

    add_key_log(

        admin_id=uid,

        product_id=product_id,

        product_name=product,

        duration=duration,

        action="GENERATE",

        quantity=added,

        details=f"Length: {length}"

    )

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    msg_id = value(uid, "generate_msg")

    await context.bot.edit_message_text(

        chat_id=update.effective_chat.id,

        message_id=msg_id,

        text=f"""✅ GENERATE SUCCESS

    ━━━━━━━━━━━━━━

    📦 Product :
    {product}

    🏷 Prefix :
    {prefix}

    ⏳ Duration :
    {duration}

    📏 Length :
    {length}

    ━━━━━━━━━━━━━━

    🔑 Generated :
    {added}

    ⚠️ Retry :
    {duplicate}
    """,

        reply_markup=InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🔑 Keys",
                    callback_data="keys"
                ),

                InlineKeyboardButton(
                    "👑 Admin Panel",
                    callback_data="admin"
                )

            ]

        ])

    )

async def import_txt(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    if not update.message.document:

        await update.message.reply_text(
            "❌ Send a TXT File."
        )

        return

    document = update.message.document

    if not document.file_name.lower().endswith(".txt"):

        await update.message.reply_text(
            "❌ Only TXT File Allowed."
        )

        return

    product = value(uid, "import_product")

    duration = value(uid, "import_duration")

    cur.execute(
        """
        SELECT id
        FROM products
        WHERE name=?
        AND duration=?
        LIMIT 1
        """,
        (
            product,
            duration
        )
    )

    row = cur.fetchone()

    if not row:

        await update.message.reply_text(
            "❌ Product Not Found."
        )

        stop_input(uid)

        return

    product_id = row["id"]

    file = await document.get_file()

    path = f"data/import_{uid}.txt"

    await file.download_to_drive(path)

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        keys = [
            x.strip()
            for x in f.readlines()
            if x.strip()
        ]

    added = 0

    duplicate = 0

    for key in keys:

        cur.execute(
            "SELECT 1 FROM keys WHERE key=?",
            (key,)
        )

        if cur.fetchone():

            duplicate += 1

            continue

        cur.execute(
            """
            INSERT INTO keys(

                product,
                duration,
                key,
                status,
                created_at

            )

            VALUES(?,?,?,?,?)

            """,
            (
                product,
                duration,
                key,
                "unused",
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        )

        added += 1

    db.commit()

    add_key_log(

        admin_id=uid,

        product_id=product_id,

        product_name=product,

        duration=duration,

        action="IMPORT",

        quantity=added,

        details=f"Duplicate: {duplicate}"

    )

    stop_input(uid)

    try:
        await update.message.delete()
    except:
        pass

    await update.message.reply_text(

    f"""✅ IMPORT SUCCESS

    ━━━━━━━━━━━━━━

    📦 Product :
    {product}

    ⏳ Duration :
    {duration}

    ━━━━━━━━━━━━━━

    📥 Imported :
    {added}

    ⚠️ Duplicate :
    {duplicate}
    """,

        reply_markup=InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "🔑 Keys",
                    callback_data="keys"
                ),

                InlineKeyboardButton(
                    "👑 Admin Panel",
                    callback_data="admin"
                )

            ]

        ])
    )

import os


@route("export_now")
async def export_now(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    uid = update.effective_user.id

    export_type = value(uid, "export_type")

    product = value(uid, "export_product")

    duration = value(uid, "export_duration")

    sql = """
        SELECT key
        FROM keys
        WHERE product=?
        AND duration=?
    """

    params = [
        product,
        duration
    ]

    if export_type == "available":

        sql += " AND status='unused'"

    elif export_type == "used":

        sql += " AND status='used'"

    sql += " ORDER BY id"

    cur.execute(sql, params)

    rows = cur.fetchall()

    if not rows:

        await edit(
            query,
            "❌ No Keys Found."
        )
        return

    os.makedirs(
        "data/exports",
        exist_ok=True
    )

    filename = (
        f"{product}_"
        f"{duration}_"
        f"{export_type}.txt"
    ).replace(" ", "_")

    path = f"data/exports/{filename}"

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        for row in rows:

            f.write(
                row["key"] + "\n"
            )

    cur.execute(
        """
        SELECT id
        FROM products
        WHERE name=?
        AND duration=?
        LIMIT 1
        """,
        (
            product,
            duration
        )
    )

    row = cur.fetchone()

    product_id = (
        row["id"]
        if row else None
    )

    add_key_log(

        admin_id=uid,

        product_id=product_id,

        product_name=product,

        duration=duration,

        action="EXPORT",

        quantity=len(rows),

        details=export_type

    )

    await context.bot.send_document(

        chat_id=query.message.chat_id,

        document=open(
            path,
            "rb"
        ),

        filename=filename,

        caption=(
            f"📤 Export Complete\n\n"
            f"📦 {product}\n"
            f"⏳ {duration}\n"
            f"📄 {export_type.upper()}\n"
            f"🔑 {len(rows)} Keys"
        )

    )

    await edit(

        query,

        "✅ Export Completed.",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="keys"
                )

            ]

        ])

    )

async def search_key_value(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    key = update.message.text.strip()

    cur.execute("""
        SELECT *
        FROM keys
        WHERE key=?
        LIMIT 1
    """, (key,))

    row = cur.fetchone()

    stop_input(uid)

    if not row:

        await update.message.reply_text(
            "❌ Key Not Found."
        )

        return

    await update.message.reply_text(

f"""🔑 KEY INFORMATION

━━━━━━━━━━━━━━

📦 Product :
{row['product']}

⏳ Duration :
{row['duration']}

🔑 Key :
{row['key']}

📌 Status :
{row['status']}

👤 Buyer :
{row['buyer_id'] or '-'}

🛒 Order :
{row['order_id'] or '-'}

🕒 Created :
{row['created_at']}

🕒 Used :
{row['used_at'] or '-'}
"""
    )


async def search_buyer_value(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    buyer = update.message.text.strip()

    cur.execute("""
        SELECT COUNT(*)
        FROM keys
        WHERE buyer_id=?
    """, (buyer,))

    total = cur.fetchone()[0]

    stop_input(uid)

    await update.message.reply_text(

f"""👤 BUYER RESULT

━━━━━━━━━━━━━━

Buyer ID :
{buyer}

━━━━━━━━━━━━━━

🔑 Total Keys :
{total}
"""
    )

async def search_order_value(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    order = update.message.text.strip()

    cur.execute("""
        SELECT *
        FROM keys
        WHERE order_id=?
    """, (order,))

    rows = cur.fetchall()

    stop_input(uid)

    if not rows:

        await update.message.reply_text(
            "❌ Order Not Found."
        )

        return

    text = f"""🛒 ORDER

━━━━━━━━━━━━━━

Order :
{order}

━━━━━━━━━━━━━━

"""

    for row in rows:

        text += (

            f"🔑 {row['key']}\n"

            f"{row['product']} | "

            f"{row['duration']}\n\n"

        )

    await update.message.reply_text(text)

async def search_product_duration(update: Update,
                                  context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    duration = update.message.text.strip()

    product = value(uid, "search_product")

    cur.execute("""
        SELECT COUNT(*)
        FROM keys
        WHERE product=?
        AND duration=?
    """, (
        product,
        duration
    ))

    total = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM keys
        WHERE product=?
        AND duration=?
        AND status='unused'
    """, (
        product,
        duration
    ))

    available = cur.fetchone()[0]

    used = total - available

    stop_input(uid)

    await update.message.reply_text(

f"""📦 PRODUCT RESULT

━━━━━━━━━━━━━━

📦 {product}

⏳ {duration}

━━━━━━━━━━━━━━

🔑 Total :
{total}

🟢 Available :
{available}

🔴 Used :
{used}
"""
    )


@route("delete_available_keys")
async def delete_available_keys(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):

    cur.execute(
        "DELETE FROM keys WHERE status='unused'"
    )

    deleted = cur.rowcount

    db.commit()

    add_key_log(

        admin_id=update.effective_user.id,

        product_id=None,

        product_name="ALL",

        duration="ALL",

        action="DELETE_AVAILABLE",

        quantity=deleted,

        details="Available Keys"

    )

    await edit(

        update.callback_query,

        f"""✅ Deleted

━━━━━━━━━━━━━━

🟢 Available Keys

Deleted : {deleted}
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="delete_keys"
                )

            ]

        ])

    )

@route("delete_used_keys")
async def delete_used_keys(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):

    cur.execute(
        "DELETE FROM keys WHERE status='used'"
    )

    deleted = cur.rowcount

    db.commit()

    add_key_log(

        admin_id=update.effective_user.id,

        product_id=None,

        product_name="ALL",

        duration="ALL",

        action="DELETE_USED",

        quantity=deleted,

        details="Used Keys"

    )

    await edit(

        update.callback_query,

        f"""✅ Deleted

━━━━━━━━━━━━━━

🔴 Used Keys

Deleted : {deleted}
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="delete_keys"
                )

            ]

        ])

    )

@route("delete_all_keys")
async def delete_all_keys(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):

    cur.execute(
        "DELETE FROM keys"
    )

    deleted = cur.rowcount

    db.commit()

    add_key_log(

        admin_id=update.effective_user.id,

        product_id=None,

        product_name="ALL",

        duration="ALL",

        action="DELETE_ALL",

        quantity=deleted,

        details="All Keys"

    )

    await edit(

        update.callback_query,

        f"""💥 ALL KEYS DELETED

━━━━━━━━━━━━━━

Deleted :

{deleted}
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="keys"
                )

            ]

        ])

    )


@route("delete_duplicate_keys")
async def delete_duplicate_keys(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):

    cur.execute("""
        DELETE FROM keys
        WHERE id NOT IN(

            SELECT MIN(id)

            FROM keys

            GROUP BY key

        )
    """)

    deleted = cur.rowcount

    db.commit()

    add_key_log(

        admin_id=update.effective_user.id,

        product_id=None,

        product_name="ALL",

        duration="ALL",

        action="DELETE_DUPLICATE",

        quantity=deleted,

        details="Duplicate Cleaner"

    )

    await edit(

        update.callback_query,

        f"""🧹 DUPLICATES REMOVED

━━━━━━━━━━━━━━

Deleted :

{deleted}
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="keys"
                )

            ]

        ])

    )

@route("delete_product_menu")
async def delete_product_menu(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT DISTINCT name
        FROM products
        WHERE status='on'
        ORDER BY name
    """)

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(

                row["name"],

                callback_data=f"delete_product_{row['name']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(

            "⬅️ Back",

            callback_data="delete_keys"

        )

    ])

    await edit(

        query,

"""🗑 DELETE PRODUCT KEYS

━━━━━━━━━━━━━━

Select Product
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("delete_product")
async def delete_product(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    product = query.data.replace(
        "delete_product_",
        ""
    )

    cur.execute("""

        SELECT
            id,
            duration

        FROM products

        WHERE name=?

        ORDER BY id

    """, (product,))

    rows = cur.fetchall()

    keyboard = []

    for row in rows:

        keyboard.append([

            InlineKeyboardButton(

                row["duration"],

                callback_data=f"delete_product_keys_{row['id']}"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(

            "⬅️ Back",

            callback_data="delete_product_menu"

        )

    ])

    await edit(

        query,

f"""📦 {product}

━━━━━━━━━━━━━━

Select Duration
""",

        InlineKeyboardMarkup(keyboard)

    )


@route("delete_product_keys")
async def delete_product_keys(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    pid = int(
        query.data.replace(
            "delete_product_keys_",
            ""
        )
    )

    cur.execute("""

        SELECT
            name,
            duration

        FROM products

        WHERE id=?

        LIMIT 1

    """, (pid,))

    row = cur.fetchone()

    if not row:

        await edit(
            query,
            "❌ Product Not Found"
        )

        return

    product = row["name"]

    duration = row["duration"]

    cur.execute("""

        DELETE FROM keys

        WHERE product=?

        AND duration=?

    """, (

        product,
        duration

    ))

    deleted = cur.rowcount

    db.commit()

    add_key_log(

        admin_id=update.effective_user.id,

        product_id=pid,

        product_name=product,

        duration=duration,

        action="DELETE_PRODUCT",

        quantity=deleted,

        details="Product Wise Delete"

    )

    await edit(

        query,

f"""✅ DELETE SUCCESS

━━━━━━━━━━━━━━

📦 {product}

⏳ {duration}

━━━━━━━━━━━━━━

🗑 Deleted :

{deleted}
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="delete_keys"
                )

            ]

        ])

    )


@route("copy_available")
async def copy_available(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    pid = int(
        query.data.replace(
            "copy_available_",
            ""
        )
    )

    cur.execute("""
        SELECT
            name,
            duration
        FROM products
        WHERE id=?
    """, (pid,))

    product = cur.fetchone()

    if not product:

        await query.answer(
            "❌ Product Not Found",
            show_alert=True
        )
        return

    cur.execute("""
        SELECT key
        FROM keys
        WHERE product=?
        AND duration=?
        AND status='unused'
        ORDER BY id
    """, (
        product["name"],
        product["duration"]
    ))

    rows = cur.fetchall()

    if not rows:

        await query.answer(
            "❌ No Available Keys",
            show_alert=True
        )
        return

    text = "\n".join(
        row["key"]
        for row in rows
    )

    if len(text) > 4000:

        with open("available_keys.txt", "w") as f:
            f.write(text)

        with open("available_keys.txt", "rb") as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=f"{product['name']}_{product['duration']}_keys.txt",
                caption=f"""🔑 AVAILABLE KEYS

━━━━━━━━━━━━━━

📦 Product : {product['name']}

⏳ Duration : {product['duration']}

📄 Total Keys : {len(rows)}
"""
            )

    else:

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"```{text}```",
            parse_mode="Markdown"
        )

    await query.answer("✅ Keys Sent")

@route("auto_delete_panel")
async def auto_delete_panel(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT value
        FROM settings
        WHERE key='auto_delete_keys'
    """)

    row = cur.fetchone()

    status = row["value"] == "1"

    text = f"""⚙️ AUTO DELETE

━━━━━━━━━━━━━━

Status :
{"🟢 ON" if status else "🔴 OFF"}

Expired keys will be deleted automatically.
"""

    keyboard = InlineKeyboardMarkup([

        [

            InlineKeyboardButton(

                "🔴 Turn OFF" if status else "🟢 Turn ON",

                callback_data="toggle_auto_delete"

            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="keys"
            ),

            InlineKeyboardButton(
                "👑 Admin",
                callback_data="admin"
            )

        ]

    ])

    await edit(
        query,
        text,
        keyboard
    )

@route("toggle_auto_delete")
async def toggle_auto_delete(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT value
        FROM settings
        WHERE key='auto_delete_keys'
    """)

    row = cur.fetchone()

    new = "0" if row["value"] == "1" else "1"

    cur.execute("""
        UPDATE settings
        SET value=?
        WHERE key='auto_delete_keys'
    """, (new,))

    db.commit()

    await query.answer(
        "🟢 Auto Delete Enabled"
        if new == "1"
        else
        "🔴 Auto Delete Disabled"
    )

    query.data = "auto_delete_panel"

    await auto_delete_panel(
        update,
        context
    )



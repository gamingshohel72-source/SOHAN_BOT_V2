import sqlite3

from datetime import datetime


DATABASE = "database.db"


db = sqlite3.connect(
    DATABASE,
    check_same_thread=False
)

db.row_factory = sqlite3.Row

cur = db.cursor()


# ==========================
# SQLITE PERFORMANCE
# ==========================

cur.execute(
    "PRAGMA journal_mode=WAL"
)

cur.execute(
    "PRAGMA synchronous=NORMAL"
)

cur.execute(
    "PRAGMA temp_store=MEMORY"
)

cur.execute(
    "PRAGMA foreign_keys=ON"
)

db.commit()


# ==========================
# DATABASE HELPERS
# ==========================

def table_exists(name):

    cur.execute(

        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name=?
        """,

        (name,)
    )

    return cur.fetchone() is not None


def column_exists(table,
                  column):

    cur.execute(

        f"PRAGMA table_info({table})"

    )

    for row in cur.fetchall():

        if row["name"] == column:

            return True

    return False


def add_column(table,
               column,
               sql_type):

    if column_exists(
        table,
        column
    ):

        return

    cur.execute(

        f"""

        ALTER TABLE {table}

        ADD COLUMN {column}

        {sql_type}

        """

    )

    db.commit()


def create_index(name,
                 table,
                 column):

    cur.execute(

        f"""

        CREATE INDEX IF NOT EXISTS

        {name}

        ON {table}({column})

        """

    )

    db.commit()


def now():

    return datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    )

# ==========================
# CREATE TABLES
# ==========================

def create_tables():

    # ----------------------
    # ADMINS
    # ----------------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS admins(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER UNIQUE,

        role TEXT DEFAULT 'normal',

        added_by INTEGER,

        created_at TEXT

    )

    """)


    # ----------------------
    # USERS
    # ----------------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY,

        username TEXT,

        first_name TEXT,

        balance INTEGER DEFAULT 0,

        banned INTEGER DEFAULT 0,

        join_date TEXT,

        ref_by INTEGER DEFAULT 0

    )

    """)


    # ----------------------
    # PRODUCTS
    # ----------------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS products(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        duration TEXT,

        price INTEGER,

        status TEXT DEFAULT 'on'

    )

    """)


    # ----------------------
    # KEYS
    # ----------------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS keys(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        product TEXT,

        duration TEXT,

        key TEXT UNIQUE,

        status TEXT DEFAULT 'available',

        user INTEGER,

        expire_at TEXT,

        expired INTEGER DEFAULT 0,

        created_at TEXT DEFAULT CURRENT_TIMESTAMP

    )

    """)


    # ----------------------
    # PAYMENTS
    # ----------------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS payments(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user INTEGER,

        amount INTEGER,

        method TEXT,

        trxid TEXT,

        screenshot TEXT,

        status TEXT DEFAULT 'pending',

        date TEXT

    )

    """)


    # ----------------------
    # ORDERS
    # ----------------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS orders(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user INTEGER,

        product TEXT,

        duration TEXT,

        amount INTEGER,

        key TEXT,

        status TEXT,

        purchase_date TEXT,

        expire_date TEXT,

        order_no TEXT,

        product_id INTEGER,

        key_id INTEGER,

        payment_id INTEGER,

        transaction_id TEXT,

        delivery_status TEXT DEFAULT 'pending',

        replaced INTEGER DEFAULT 0,

        replaced_key_id INTEGER,

        admin_id INTEGER,

        note TEXT,

        created_at TEXT,

        completed_at TEXT

    )

    """)


    # ----------------------
    # CONTACTS
    # ----------------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS contacts(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        type TEXT,

        display_name TEXT,

        username TEXT UNIQUE,

        status INTEGER DEFAULT 1,

        created_at TEXT

    )

    """)


    # ----------------------
    # SETTINGS
    # ----------------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS settings(

        key TEXT PRIMARY KEY,

        value TEXT

    )

    """)

    cur.execute("""
    INSERT OR IGNORE INTO settings(
        key,
        value
    )
    VALUES(
        'auto_delete_keys',
        '1'
    )
    """)


    # ----------------------
    # LOGS
    # ----------------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS logs(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        admin_id INTEGER,

        action TEXT,

        details TEXT,

        date TEXT DEFAULT CURRENT_TIMESTAMP

    )

    """)


    # ----------------------
    # KEY LOGS
    # ----------------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS key_logs(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        admin_id INTEGER,

        product_id INTEGER,

        product_name TEXT,

        duration TEXT,

        action TEXT,

        quantity INTEGER,

        details TEXT,

        created_at TEXT

    )

    """)




    # ----------------------
    # REDEEM
    # ----------------------

    cur.execute("""
    CREATE TABLE IF NOT EXISTS redeem(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        code TEXT UNIQUE NOT NULL,

        amount INTEGER NOT NULL,

        limit_count INTEGER DEFAULT 1,

        used_count INTEGER DEFAULT 0,

        per_user INTEGER DEFAULT 1,

        expire_at TEXT,

        status INTEGER DEFAULT 1,

        created_at TEXT DEFAULT CURRENT_TIMESTAMP

    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS redeem_history(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        redeem_id INTEGER,

        user_id INTEGER,

        code TEXT,

        amount INTEGER,

        used_at TEXT DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # ----------------------
    # PAYMENT METHODS
    # ----------------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS payment_methods(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT UNIQUE,

        number TEXT,

        status INTEGER DEFAULT 1

    )

    """)

    # =========================
    # BROADCAST HISTORY
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS broadcast_history(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        admin INTEGER,

        type TEXT,

        content TEXT,

        total INTEGER DEFAULT 0,

        success INTEGER DEFAULT 0,

        failed INTEGER DEFAULT 0,

        created_at TEXT

    )
    """)

    db.commit()

# ==========================
# DATABASE UPGRADE
# ==========================

def upgrade_database():

    # ----------------------
    # USERS
    # ----------------------

    add_column(
        "users",
        "language",
        "TEXT"
    )

    add_column(
        "users",
        "last_seen",
        "TEXT"
    )

    add_column(
        "users",
        "total_purchase",
        "INTEGER DEFAULT 0"
    )

    # ----------------------
    # PRODUCTS
    # ----------------------

    add_column(
        "products",
        "prefix",
        "TEXT"
    )

    add_column(
        "products",
        "category",
        "TEXT"
    )

    add_column(
        "products",
        "description",
        "TEXT"
    )

    add_column(
        "products",
        "sort_order",
        "INTEGER DEFAULT 0"
    )

    # ----------------------
    # KEYS
    # ----------------------

    add_column(
        "keys",
        "buyer_id",
        "INTEGER"
    )

    add_column(
        "keys",
        "order_id",
        "INTEGER"
    )

    add_column(
        "keys",
        "used_at",
        "TEXT"
    )

    add_column(
        "keys",
        "created_at",
        "TEXT"
    )

    add_column(
        "keys",
        "admin_id",
        "INTEGER"
    )

    # ----------------------
    # PAYMENTS
    # ----------------------

    add_column(
        "payments",
        "admin_id",
        "INTEGER"
    )

    add_column(
        "payments",
        "note",
        "TEXT"
    )

    add_column(
        "payments",
        "created_at",
        "TEXT"
    )

    add_column(
        "payments",
        "completed_at",
        "TEXT"
    )

    # ----------------------
    # ORDERS
    # ----------------------

    add_column(
        "orders",
        "order_no",
        "TEXT"
    )

    add_column(
        "orders",
        "product_id",
        "INTEGER"
    )

    add_column(
        "orders",
        "key_id",
        "INTEGER"
    )

    add_column(
        "orders",
        "payment_id",
        "INTEGER"
    )

    add_column(
        "orders",
        "transaction_id",
        "TEXT"
    )

    add_column(
        "orders",
        "delivery_status",
        "TEXT DEFAULT 'pending'"
    )

    add_column(
        "orders",
        "replaced",
        "INTEGER DEFAULT 0"
    )

    add_column(
        "orders",
        "replaced_key_id",
        "INTEGER"
    )

    add_column(
        "orders",
        "admin_id",
        "INTEGER"
    )

    add_column(
        "orders",
        "note",
        "TEXT"
    )

    add_column(
        "orders",
        "created_at",
        "TEXT"
    )

    add_column(
        "orders",
        "completed_at",
        "TEXT"
    )

    add_column(
        "orders",
        "expire_at",
        "TEXT"
    )

    add_column(
        "orders",
        "user_id",
        "INTEGER"
    )

    # ----------------------
    # INDEXES
    # ----------------------

    create_index(
        "idx_keys_status",
        "keys",
        "status"
    )

    create_index(
        "idx_orders_user",
        "orders",
        "user"
    )

    create_index(
        "idx_payments_status",
        "payments",
        "status"
    )

    db.commit()

# ==========================
# DEFAULT DATA
# ==========================

def insert_defaults():

    # ----------------------
    # DEFAULT ADMIN
    # ----------------------

    cur.execute(

        """
        INSERT OR IGNORE INTO admins(

            user_id,

            role,

            added_by,

            created_at

        )

        VALUES(

            ?, ?, ?, ?

        )

        """,

        (

            8153757163,

            "premium",

            8153757163,

            now()

        )

    )

    # ----------------------
    # PAYMENT METHODS
    # ----------------------

    methods = [

        ("bKash", ""),

        ("Nagad", ""),

        ("Rocket", "")

    ]

    for name, number in methods:

        cur.execute(

            """
            INSERT OR IGNORE
            INTO payment_methods(

                name,

                number

            )

            VALUES(?,?)

            """,

            (

                name,

                number

            )

        )

    # ----------------------
    # CONTACTS
    # ----------------------

    contacts = [

        (

            "support",

            "Support",

            "@GhPrimeAdmin"

        ),

        (

            "channel",

            "Update",

            "ghprime_update"

        )

    ]

    for ctype, display, username in contacts:

        cur.execute(

            """
            INSERT OR IGNORE INTO contacts(

                type,

                display_name,

                username,

                created_at

            )

            VALUES(?,?,?,?)

            """,

            (

                ctype,

                display,

                username,

                now()

            )

        )

    # ----------------------
    # SETTINGS
    # ----------------------

    defaults = {

        "bot_name": "SOHAN BOT",

        "join_bonus": "0",

        "maintenance": "off",

        "payment_number": "",

        "support": "",

        "channel": "",

        "welcome": "👋 Welcome",

        "rules": "No Rules Added."

    }

    for key, value in defaults.items():

        cur.execute(

            """
            INSERT OR IGNORE
            INTO settings(

                key,

                value

            )

            VALUES(?,?)

            """,

            (

                key,

                value

            )

        )

    db.commit()

def is_admin(user_id):

    cur.execute(
        """
        SELECT 1
        FROM admins
        WHERE user_id=?
        """,
        (user_id,)
    )

    return cur.fetchone() is not None

def is_banned(user_id):

    cur.execute(
        """
        SELECT banned
        FROM users
        WHERE id=?
        """,
        (user_id,)
    )

    row = cur.fetchone()

    if not row:
        return False

    return row["banned"] == 1

# ==========================
# INITIALIZE DATABASE
# ==========================

def init_database():

    create_tables()

    upgrade_database()

    insert_defaults()

    db.commit()

    print(

        "✅ Database Ready"

    )


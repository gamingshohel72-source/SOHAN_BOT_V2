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
    value,
    clear
)

@route("admin_list")
async def admin_list(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cur.execute("""
        SELECT
            id,
            user_id,
            role
        FROM admins
        ORDER BY id ASC
    """)

    rows = cur.fetchall()

    keyboard = []

    if rows:

        for row in rows:

            keyboard.append([

                InlineKeyboardButton(

                    f"👤 {row['user_id']} ({row['role']})",

                    callback_data=f"admin_info_{row['id']}"

                )

            ])

    else:

        keyboard.append([

            InlineKeyboardButton(

                "No Admin Found",

                callback_data="none"

            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "➕ Add Admin",
            callback_data="add_admin"
        )

    ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="admin"
        )

    ])

    await edit(

        query,

f"""👑 ADMIN LIST

━━━━━━━━━━━━━━

Total Admin :

{len(rows)}
""",

        InlineKeyboardMarkup(keyboard)

    )

@route("admin_info_")
async def admin_info(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    admin_id = int(
        query.data.replace(
            "admin_info_",
            ""
        )
    )

    set(
        update.effective_user.id,
        "selected_admin",
        admin_id
    )

    cur.execute(
        """
        SELECT *
        FROM admins
        WHERE id=?
        """,
        (admin_id,)
    )

    row = cur.fetchone()

    if not row:

        await query.answer(
            "❌ Admin Not Found",
            show_alert=True
        )

        return

    text = f"""👑 ADMIN INFORMATION

━━━━━━━━━━━━━━

🆔 Admin ID
➜ {row['id']}

👤 Telegram ID
➜ {row['user_id']}

📱 Telegram ID
➜ {row['user_id']}

🛡 Role
➜ {row['role']}

📅 Added
➜ {row['created_at']}
"""

    keyboard = InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "🛡 Change Role",
                callback_data="change_admin_role"
            )

        ],

        [

            InlineKeyboardButton(
                "🗑 Remove Admin",
                callback_data="remove_admin"
            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="admin_list"
            ),

            InlineKeyboardButton(
                "🏠 Admin",
                callback_data="admin"
            )

        ]

    ])

    await edit(

        query,

        text,

        keyboard

    )

@route("add_admin")
async def add_admin(update: Update,
                    context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    start_input(
        update.effective_user.id,
        "add_admin"
    )

    msg = await edit(

        query,

"""➕ ADD ADMIN

━━━━━━━━━━━━━━

Send:

User ID
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="admin_list"
                )

            ]

        ])

    )

    set(
        update.effective_user.id,
        "admin_add_msg",
        msg.message_id
    )

async def save_add_admin(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    admin_id = update.effective_user.id

    try:

        uid = int(
            update.message.text.strip()
        )

    except:

        await update.message.reply_text(
            "❌ Invalid User ID"
        )

        return

    cur.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (uid,)
    )

    user = cur.fetchone()

    if not user:

        await update.message.reply_text(
            "❌ User Not Found"
        )

        return

    cur.execute(
        """
        SELECT 1
        FROM admins
        WHERE user_id=?
        """,
        (uid,)
    )

    if cur.fetchone():

        await update.message.reply_text(
            "❌ User is already an admin."
        )

        return

    set(
        admin_id,
        "new_admin",
        uid
    )

    stop_input(admin_id)

    try:
        await update.message.delete()
    except:
        pass

    msg_id = value(
        admin_id,
        "admin_add_msg"
    )

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=msg_id,
        text="""✅ USER FOUND

    ━━━━━━━━━━━━━━

    Select Admin Role
    """,
        reply_markup=InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "👑 Owner",
                    callback_data="admin_role_owner"
                )

            ],

            [

                InlineKeyboardButton(
                    "🛡 Manager",
                    callback_data="admin_role_manager"
                ),

                InlineKeyboardButton(
                    "🎧 Support",
                    callback_data="admin_role_support"
                )

            ],

            [

                InlineKeyboardButton(
                    "👮 Moderator",
                    callback_data="admin_role_moderator"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="admin_list"
                )

            ]

        ])
    )

@route("change_admin_role")
async def change_admin_role(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await edit(

        query,

"""🛡 CHANGE ADMIN ROLE

━━━━━━━━━━━━━━

Select New Role
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "👑 Owner",
                    callback_data="admin_role_owner"
                ),

                InlineKeyboardButton(
                    "⚙️ Manager",
                    callback_data="admin_role_manager"
                )

            ],

            [

                InlineKeyboardButton(
                    "🛠 Support",
                    callback_data="admin_role_support"
                ),

                InlineKeyboardButton(
                    "🛡 Moderator",
                    callback_data="admin_role_moderator"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="admin_list"
                )

            ]

        ])

    )


@route("admin_role")
async def save_admin_role(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    role = query.data.replace(
        "admin_role_",
        ""
    )

    current_admin = update.effective_user.id

    new_admin = value(
        current_admin,
        "new_admin"
    )

    selected_admin = value(
        current_admin,
        "selected_admin"
    )

    print("CURRENT_ADMIN =", current_admin)
    print("NEW_ADMIN =", new_admin)
    print("SELECTED_ADMIN =", selected_admin)
    print("ROLE =", role)

    if new_admin:

        cur.execute(
            """
            INSERT INTO admins(
                user_id,
                role,
                added_by,
                created_at
            )
            VALUES(?,?,?,datetime('now'))
            """,
            (
                new_admin,
                role,
                current_admin
            )
        )

        db.commit()

        print("ADMIN INSERTED")

        set(
            current_admin,
            "new_admin",
            None
        )

        await edit(

            query,

f"""✅ ADMIN ADDED

━━━━━━━━━━━━━━

👤 User ID : {new_admin}

🛡 Role : {role}
""",

            InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "👑 Admin List",
                        callback_data="admin_list"
                    )

                ]

            ])

        )

        return

    if selected_admin:

        cur.execute(
            """
            UPDATE admins
            SET role=?
            WHERE id=?
            """,
            (
                role,
                selected_admin
            )
        )

        db.commit()

        await edit(

            query,

f"""✅ ROLE UPDATED

━━━━━━━━━━━━━━

🛡 New Role

{role}
""",

            InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data=f"admin_info_{selected_admin}"
                    )

                ]

            ])

        )

@route("remove_admin")
async def remove_admin(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    admin_id = value(
        update.effective_user.id,
        "selected_admin"
    )

    if not admin_id:

        await query.answer(
            "❌ No admin selected.",
            show_alert=True
        )

        return

    await edit(

        query,

"""🗑 REMOVE ADMIN

━━━━━━━━━━━━━━

Are you sure you want to remove this admin?
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "✅ Yes",
                    callback_data="confirm_remove_admin"
                ),

                InlineKeyboardButton(
                    "❌ No",
                    callback_data=f"admin_info_{admin_id}"
                )

            ]

        ])

    )


@route("confirm_remove_admin")
async def confirm_remove_admin(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    admin_id = value(
        update.effective_user.id,
        "selected_admin"
    )

    if not admin_id:

        await query.answer(
            "❌ No admin selected.",
            show_alert=True
        )

        return

    cur.execute(
        """
        DELETE FROM admins
        WHERE id=?
        """,
        (admin_id,)
    )

    db.commit()

    set(
        update.effective_user.id,
        "selected_admin",
        None
    )

    await edit(

        query,

"""✅ ADMIN REMOVED

━━━━━━━━━━━━━━

The selected admin has been removed successfully.
""",

        InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "👑 Admin List",
                    callback_data="admin_list"
                )

            ],

            [

                InlineKeyboardButton(
                    "🏠 Admin Panel",
                    callback_data="admin"
                )

            ]

        ])

    )

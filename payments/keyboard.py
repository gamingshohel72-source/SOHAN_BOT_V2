from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CopyTextButton
)

def methods_keyboard(rows):

    keyboard = []

    for row in rows:

        keyboard.append([
            InlineKeyboardButton(
                f"💳 {row['name']}",
                callback_data=f"paymethod_{row['id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "❌ Cancel",
            callback_data="payment_cancel"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def continue_menu():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "➡️ Continue",
                callback_data="payment_continue"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="add_balance"
            ),

            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="payment_cancel"
            )

        ]

    ])


def back_cancel(back):

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data=back
            ),

            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="payment_cancel"
            )

        ]

    ])


def confirm():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "✅ Submit",
                callback_data="payment_submit"
            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="payment_back"
            ),

            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="payment_cancel"
            )

        ]

    ])


def approve(pid):

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve_{pid}"
            ),

            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_{pid}"
            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="payments"
            )

        ]

    ])


def method_page(mid, number=None):

    keyboard = []

    # =====================================================
    # COPY NUMBER
    # =====================================================

    if number:

        keyboard.append([

            InlineKeyboardButton(
                "📋 Copy Number",
                copy_text=CopyTextButton(
                    text=str(number)
                )
            )

        ])

    # =====================================================
    # CONTINUE
    # =====================================================

    keyboard.append([

        InlineKeyboardButton(
            "➡️ Continue",
            callback_data="payment_continue"
        )

    ])

    # =====================================================
    # BACK + CANCEL
    # =====================================================

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="add_balance"
        ),

        InlineKeyboardButton(
            "❌ Cancel",
            callback_data="payment_cancel"
        )

    ])

    return InlineKeyboardMarkup(keyboard)

def home():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "🏠 Home",
                callback_data="home"
            )

        ]

    ])

def admin_back():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="admin"
            )

        ]

    ])

from telegram import Update
from telegram.ext import ContextTypes

import os
import shutil

from input import current_input

from keys import import_txt

# Future
# from products import import_products
# from users import import_users
# from orders import import_orders
# from backup import restore_backup


MAX_FILE_SIZE = 20 * 1024 * 1024


async def document_handler(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    document = update.message.document

    if not document:
        return

    if document.file_size > MAX_FILE_SIZE:

        await update.message.reply_text(

"""❌ FILE TOO LARGE

━━━━━━━━━━━━━━

Maximum File Size

20 MB
"""

        )

        return

    uid = update.effective_user.id

    mode = current_input(uid)

    if not mode:

        await update.message.reply_text(

"""❌ No Active Input"""

        )
        return

async def invalid_file(update: Update,
                       text):

    await update.message.reply_text(

f"""❌ INVALID FILE

━━━━━━━━━━━━━━

{text}
"""

    )


def is_txt(document):

    if not document:
        return False

    if not document.file_name:
        return False

    return document.file_name.lower().endswith(
        ".txt"
    )


def is_csv(document):

    if not document:
        return False

    if not document.file_name:
        return False

    return document.file_name.lower().endswith(
        ".csv"
    )


def is_zip(document):

    if not document:
        return False

    if not document.file_name:
        return False

    return document.file_name.lower().endswith(
        ".zip"
    )


def is_image(document):

    if not document:
        return False

    if not document.mime_type:
        return False

    return document.mime_type.startswith(
        "image/"
    )


def ensure_folder(folder):

    os.makedirs(

        folder,

        exist_ok=True

    )


async def download_document(document,
                            folder):

    ensure_folder(folder)

    filename = document.file_name.replace(
        " ",
        "_"
    )

    path = os.path.join(
        folder,
        filename
    )

    tg_file = await document.get_file()

    await tg_file.download_to_drive(
        path
    )

    return path


def delete_file(path):

    try:

        if os.path.exists(path):

            os.remove(path)

    except:

        pass

async def upload_logo(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not is_image(document):

        await invalid_file(
            update,
            "Only PNG/JPG Image Allowed."
        )

        return

    path = await download_document(
        document,
        "data/logo"
    )

    await update.message.reply_text(

f"""✅ LOGO UPDATED

━━━━━━━━━━━━━━

📁 {path}
"""
    )


async def upload_banner(update: Update,
                        context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not is_image(document):

        await invalid_file(
            update,
            "Only PNG/JPG Image Allowed."
        )

        return

    path = await download_document(
        document,
        "data/banner"
    )

    await update.message.reply_text(

f"""✅ BANNER UPDATED

━━━━━━━━━━━━━━

📁 {path}
"""
    )


async def upload_terms(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not is_txt(document):

        await invalid_file(
            update,
            "Only TXT File Allowed."
        )

        return

    path = await download_document(
        document,
        "data/terms"
    )

    await update.message.reply_text(

f"""✅ TERMS UPDATED

━━━━━━━━━━━━━━

📁 {path}
"""
    )


async def restore_backup(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not is_zip(document):

        await invalid_file(
            update,
            "Only ZIP Backup Allowed."
        )

        return

    path = await download_document(
        document,
        "data/backup"
    )

    await update.message.reply_text(

f"""✅ BACKUP RECEIVED

━━━━━━━━━━━━━━

📁 {path}

Restore Process Ready.
"""
    )


async def upload_broadcast_media(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    path = await download_document(
        document,
        "data/broadcast"
    )

    await update.message.reply_text(

f"""✅ MEDIA SAVED

━━━━━━━━━━━━━━

📁 {path}
"""
    )

    # ==========================
    # TXT IMPORT
    # ==========================

    if mode == "import_txt":

        if not is_txt(document):

            await invalid_file(
                update,
                "Only TXT File Allowed."
            )

            return

        await import_txt(
            update,
            context
        )

        return

    # ==========================
    # CSV IMPORT
    # ==========================

    elif mode == "import_products":

        pass

    elif mode == "import_users":

        pass

    elif mode == "import_orders":

        pass

    # ==========================
    # BACKUP
    # ==========================

    elif mode == "restore_backup":

        pass

    # ==========================
    # SETTINGS
    # ==========================

    elif mode == "upload_logo":

        pass

    elif mode == "upload_banner":

        pass

    elif mode == "upload_terms":

        pass

    elif mode == "broadcast_media":

        pass

    else:

        await invalid_file(

            update,

            "Unknown Document Request."

        )



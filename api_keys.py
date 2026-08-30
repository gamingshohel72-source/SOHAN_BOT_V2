"""GH PRIME Remote API Key Manager.

This module keeps the existing Telegram UI/callback namespace but stores and
manages keys through the remote GH PRIME Key API instead of the bot's local
api_keys SQLite table.

API:
    GET  /health
    POST /generate
    GET  /verify
    GET  /keys
    POST /keys/delete
    POST /keys/revoke
    GET  /stats

Authentication:
    KEY_API_SECRET environment variable, or .api_secret beside this file.
"""

import os
import requests

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from routes import route
from utils import edit
from input import start_input, stop_input, current_input
from telegram import CopyTextButton
from config import KEY_API_SECRET

# ---------------------------------------------------------------------------
# Remote API configuration
# ---------------------------------------------------------------------------

from config import KEY_API_URL, KEY_API_SECRET


KEY_API_URL = KEY_API_URL.strip().rstrip("/")
KEY_API_SECRET = KEY_API_SECRET.strip().replace("\ufeff", "")

class KeyAPIError(Exception):
    pass


def _headers():
    headers = {"Content-Type": "application/json"}
    if KEY_API_SECRET:
        headers["Authorization"] = f"Bearer {KEY_API_SECRET}"
    return headers


def _request(method, path, **kwargs):
    url = f"{KEY_API_URL}{path}"
    kwargs.setdefault("headers", _headers())
    kwargs.setdefault("timeout", 20)

    try:
        response = requests.request(method, url, **kwargs)
    except requests.RequestException as e:
        raise KeyAPIError(f"Connection failed: {e}") from e

    try:
        data = response.json()
    except Exception:
        data = {"success": False, "error": response.text}

    if not response.ok:
        error = data.get("error") if isinstance(data, dict) else None
        raise KeyAPIError(
            f"API HTTP {response.status_code}: {error or response.text}"
        )

    return data


def _api_stats():
    return _request("GET", "/stats")


def _api_keys(q="", product="", status="", limit=100):
    params = {
        "q": q or "",
        "product": product or "",
        "status": status or "",
        "limit": int(limit),
    }
    return _request("GET", "/keys", params=params)


def _api_generate(product, duration, order_id="", customer_id=""):
    return _request(
        "POST",
        "/generate",
        json={
            "product": product,
            "duration": duration,
            "order_id": order_id,
            "customer_id": customer_id,
        },
    )


def _api_delete(keys):
    results = []
    for key in keys:
        try:
            data = _request("DELETE", "/keys/" + str(key))
            results.append((key, True, data))
        except Exception as e:
            results.append((key, False, str(e)))
    return results


def _api_revoke(key):
    return _request("POST", "/keys/revoke", json={"key": key})


def _extract_keys(data):
    """Best-effort extraction because the API may return slightly different shapes."""
    if isinstance(data, dict):
        for field in ("key", "api_key"):
            if data.get(field):
                return [str(data[field])]

        for field in ("keys", "data", "result"):
            value = data.get(field)
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                found = _extract_keys(value)
                if found:
                    return found

    if isinstance(data, list):
        return data

    return []


def _format_key_item(item):
    if isinstance(item, str):
        return f"🔑 {item}"

    if isinstance(item, dict):
        key = (
            item.get("key")
            or item.get("api_key")
            or item.get("value")
            or "-"
        )
        product = item.get("product", "-")
        duration = item.get("duration", "-")
        status = item.get("status", "-")
        expires = item.get("expire_at") or item.get("expires_at") or "-"
        item_id = item.get("id", "-")

        return (
            f"#{item_id}  {str(status).upper()}\n"
            f"🔑 {key}\n"
            f"📦 Product: {product}\n"
            f"⏳ Duration: {duration}\n"
            f"⌛ Expires: {expires}"
        )

    return f"🔑 {item}"


def _menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚡ Generate", callback_data="api_keys_generate"),
            InlineKeyboardButton("🔍 Search", callback_data="api_keys_search"),
        ],
        [
            InlineKeyboardButton("📋 View", callback_data="api_keys_view"),
            InlineKeyboardButton("🗑 Delete", callback_data="api_keys_delete"),
        ],
        [
            InlineKeyboardButton("🚫 Revoke", callback_data="api_keys_revoke"),
            InlineKeyboardButton("📊 Statistics", callback_data="api_keys_stats"),
        ],
        [InlineKeyboardButton("⬅️ Back", callback_data="admin")],
    ])


@route("api_keys")
async def api_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        data = _api_stats()
        total = data.get("total_keys", data.get("total", data.get("count", 0)))
        active = data.get("active_keys", data.get("active", 0))
        revoked = data.get("revoked_keys", data.get("revoked", 0))

        text = (
            "🔐 API KEY MANAGER\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🔑 Total API Keys : {total}\n"
            f"🟢 Active         : {active}\n"
            f"🔴 Revoked        : {revoked}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🟢 Connected to GH PRIME Key API"
        )
    except Exception as e:
        text = (
            "🔐 API KEY MANAGER\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🔴 API CONNECTION FAILED\n\n"
            f"{e}\n\n"
            f"API: {KEY_API_URL}"
        )

    await edit(query, text, _menu())


@route("api_keys_generate")
async def api_keys_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    start_input(update.effective_user.id, "api_keys_generate")

    await edit(
        query,
        "⚡ GENERATE PRODUCT KEY\n\n"
        "Send in this format:\n\n"
        "Product | Duration\n\n"
        "Example:\n"
        "DRIP CLIENT NON-ROOT | 1day\n\n"
        "For multiple keys, send one request per line.",
        InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="api_keys")]
        ]),
    )


@route("api_keys_search")
async def api_keys_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    start_input(update.effective_user.id, "api_keys_search")

    await edit(
        query,
        "🔍 SEARCH API KEY\n\n"
        "Send API key, product name, customer ID,\n"
        "or order ID.",
        InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="api_keys")]
        ]),
    )


@route("api_keys_delete")
async def api_keys_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    start_input(update.effective_user.id, "api_keys_delete")

    await edit(
        query,
        "🗑 DELETE API KEYS\n\n"
        "Send one or multiple keys.\n"
        "Separate multiple keys with commas.",
        InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="api_keys")]
        ]),
    )


@route("api_keys_revoke")
async def api_keys_revoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    start_input(update.effective_user.id, "api_keys_revoke")

    await edit(
        query,
        "🚫 REVOKE API KEY\n\n"
        "Send the exact product key to revoke.",
        InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="api_keys")]
        ]),
    )


@route("api_keys_view")
async def api_keys_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        data = _api_keys(limit=100)
        rows = data.get("keys", []) if isinstance(data, dict) else []

        if not rows:
            text = "📋 API KEYS\n\nNo keys found in the remote API."
        else:
            lines = ["📋 API KEYS", "", "━━━━━━━━━━━━━━━━━━"]
            for item in rows:
                lines.append(_format_key_item(item))
                lines.append("")
            text = "\n".join(lines)

    except Exception as e:
        text = f"❌ Could not load API keys.\n\n{e}"

    keyboard = []

    for item in rows:
        if isinstance(item, dict):

            key = (
                item.get("key")
                or item.get("api_key")
                or item.get("value")
            )

            if key:
                keyboard.append([
                    InlineKeyboardButton(
                        "📋 Copy Key",
                        copy_text=CopyTextButton(
                            text=str(key)
                        )
                    )
                ])


    keyboard.append(
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="api_keys"
            )
        ]
    )

    markup = InlineKeyboardMarkup(keyboard)

    await edit(query, text, markup)


@route("api_keys_stats")
async def api_keys_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        data = _api_stats()
        total = data.get("total_keys", data.get("total", data.get("count", 0)))
        active = data.get("active_keys", data.get("active", 0))
        revoked = data.get("revoked_keys", data.get("revoked", 0))
        today = data.get("generated_today", data.get("generatedToday", 0))

        text = (
            "📊 API KEY STATISTICS\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🔑 Total : {total}\n"
            f"🟢 Active : {active}\n"
            f"🔴 Revoked : {revoked}\n"
            f"⏳ Expired : {data.get("expired_keys", 0)}\n"
            f"⚡ Generated Today : {today}"
        )
    except Exception as e:
        text = f"❌ Statistics unavailable.\n\n{e}"

    await edit(query, text, _menu())


async def handle_api_key_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Called by bot.py's normal message input handler for api_keys_* states."""
    uid = update.effective_user.id
    mode = current_input(uid)

    if not mode or not mode.startswith("api_keys_"):
        return False

    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("❌ Please send text input.")
        return True

    # ---------------------------------------------------------------
    # GENERATE
    # ---------------------------------------------------------------
    if mode == "api_keys_generate":
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        created = []
        errors = []

        for line in lines:
            if "|" not in line:
                errors.append(
                    f"❌ Invalid format: {line}\nUse Product | Duration"
                )
                continue

            product, duration = [x.strip() for x in line.split("|", 1)]

            if not product or not duration:
                errors.append(f"❌ Invalid request: {line}")
                continue

            try:
                data = _api_generate(product, duration)
                keys = _extract_keys(data)

                if keys:
                    for key in keys:
                        created.append(
                            f"🔑 {key}\n📦 {product}\n⏳ {duration}"
                        )
                else:
                    created.append(
                        f"✅ Generated\n📦 {product}\n⏳ {duration}\n"
                        f"{data}"
                    )
            except Exception as e:
                errors.append(f"❌ {product} | {duration}\n{e}")

        stop_input(uid)

        parts = []
        if created:
            parts.append("⚡ GENERATED KEYS\n\n" + "\n\n".join(created))
        if errors:
            parts.append("ERRORS\n\n" + "\n\n".join(errors))

        await update.message.reply_text("\n\n━━━━━━━━━━━━━━━━━━\n\n".join(parts))
        return True

    # ---------------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------------
    if mode == "api_keys_search":
        stop_input(uid)

        try:
            data = _api_keys(q=text, limit=100)
            rows = data.get("keys", []) if isinstance(data, dict) else []

            if not rows:
                await update.message.reply_text(
                    "❌ No keys found in the remote API."
                )
                return True

            lines = ["🔍 SEARCH RESULTS", ""]
            for item in rows:
                lines.append(_format_key_item(item))
                lines.append("")

            await update.message.reply_text("\n".join(lines))
        except Exception as e:
            await update.message.reply_text(f"❌ Search failed.\n\n{e}")

        return True

    # ---------------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------------
    if mode == "api_keys_delete":
        parts = [p.strip() for p in text.replace("\n", ",").split(",") if p.strip()]

        try:
            results = _api_delete(parts)
            stop_input(uid)

            deleted = sum(1 for _, ok, _ in results if ok)
            failed = len(results) - deleted

            lines = [
                "🗑 DELETE RESULT",
                "",
                f"✅ Deleted: {deleted}",
                f"❌ Failed: {failed}",
            ]

            for key, ok, result in results:
                if ok:
                    lines.append(f"\n✅ {key}")
                else:
                    lines.append(f"\n❌ {key}\n{result}")

            await update.message.reply_text("\n".join(lines))
        except Exception as e:
            stop_input(uid)
            await update.message.reply_text(f"❌ Delete failed.\n\n{e}")

        return True

    # ---------------------------------------------------------------
    # REVOKE
    # ---------------------------------------------------------------
    if mode == "api_keys_revoke":
        try:
            data = _api_revoke(text)
            success = data.get("success", False) if isinstance(data, dict) else False
            stop_input(uid)

            await update.message.reply_text(
                "🚫 API key revoked successfully."
                if success
                else f"❌ API key was not revoked.\n\n{data}"
            )
        except Exception as e:
            stop_input(uid)
            await update.message.reply_text(f"❌ Revoke failed.\n\n{e}")

        return True

    return False

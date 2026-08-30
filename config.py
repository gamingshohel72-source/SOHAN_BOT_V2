# ============ BOT CONFIG ============

import os

BOT_NAME = "GH PRIME STORE"

BUILD = 1

TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = int(os.getenv("OWNER_ID", "8153757163"))

PAYMENT_NUMBER = "01823146531"

JOIN_BONUS = 0

SUPPORT = "t.me/GhPrimeAdmin"

CHANNEL = "https://t.me/ghprime_update"

AUTO_DELETE = 30


# ============ KEY API ============

KEY_API_SECRET = os.getenv(
    "KEY_API_SECRET",
    "Ghprime.osjsvosbsobzkvsibs"
)

KEY_API_URL = "https://keyapi1.netlify.app"

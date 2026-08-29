# SOHAN BOT + KEY API integration

Architecture:
- Existing `keys.py` Key Manager remains local and unchanged.
- `api_keys.py` is a Telegram client for the existing KEY API website.
- Product purchases call the real API `POST /generate`.
- The API website/database is the source of truth for generated product keys.
- API-generated key records automatically contain product, duration, order_id and customer_id.
- Bot mirrors the completed payment/order in its own order ledger.
- API Key Manager operations call the existing API routes:
  GET /keys
  GET /keys/search?key=...
  POST /keys/<key>/revoke
  DELETE /keys/<key>
  GET /stats
  POST /generate

Configuration:
Set these environment variables for the bot:
  KEY_API_URL=http://127.0.0.1:5000
  KEY_API_SECRET=<same secret as key-api/.api_secret>

If the bot and key-api are sibling folders, api_keys.py also tries:
  ../key-api/.api_secret

Do not put the bot token or API secret into source control.

Modified files:
- api_keys.py
- shop.py
- bot.py

The existing key-api website source/database is not modified by this patch.

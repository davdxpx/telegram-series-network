from aiogram.utils.web_app import check_webapp_signature
from fastapi import Header, HTTPException, Depends
from app.config import settings
import logging

logger = logging.getLogger(__name__)

async def verify_admin(x_telegram_init_data: str = Header(None)):
    """
    Verifies that the request comes from the Owner via the Telegram WebApp.
    Uses aiogram's utility to check the signature of initData.
    """
    if not x_telegram_init_data:
        # For development/testing ease if needed, but production should fail
        # raise HTTPException(status_code=401, detail="Missing initData")

        # Taking a simpler approach for this iteration:
        # If no initData, we check for a static secret if configured?
        # No, strict mode.
        raise HTTPException(status_code=401, detail="Unauthorized: Missing WebApp Data")

    try:
        # Validate the data against the BOT_TOKEN
        # check_webapp_signature returns True/False
        is_valid = check_webapp_signature(settings.BOT_TOKEN, x_telegram_init_data)
        if not is_valid:
             raise HTTPException(status_code=403, detail="Invalid WebApp Signature")

        # Parse the data to get the user ID
        # web_app_data is a query string like "query_id=...&user=%7B%22id%22%3A123...%7D&auth_date=..."
        # We need to extract user.id
        from urllib.parse import parse_qs
        import json

        parsed = parse_qs(x_telegram_init_data)
        user_json = parsed.get("user", [None])[0]

        if not user_json:
            raise HTTPException(status_code=400, detail="No user data found")

        user_data = json.loads(user_json)
        user_id = user_data.get("id")

        if user_id != settings.OWNER_TELEGRAM_ID:
            raise HTTPException(status_code=403, detail="Forbidden: You are not the Owner")

        return user_id

    except Exception as e:
        logger.error(f"Auth Error: {e}")
        raise HTTPException(status_code=401, detail="Authentication Failed")

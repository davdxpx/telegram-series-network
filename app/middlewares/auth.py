from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from typing import Callable, Dict, Any, Awaitable
from app.models import User, AdminSettings
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseMiddleware):
    """
    Middleware to:
    1. Ensure user exists in DB.
    2. Check if user is banned.
    3. Determine role (Owner overrides everything).
    """
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:

        # Only process for Message and CallbackQuery updates that have a user
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        telegram_id = user.id

        # 1. Fetch or Create User
        db_user = await User.find_one(User.telegram_id == telegram_id)

        if not db_user:
            # Check if it's the owner (auto-admin)
            role = "viewer"
            if telegram_id == settings.OWNER_TELEGRAM_ID:
                role = "owner"

            db_user = User(
                telegram_id=telegram_id,
                username=user.username,
                full_name=user.full_name,
                role=role
            )
            await db_user.create()
            logger.info(f"New user registered: {user.full_name} ({telegram_id}) as {role}")

        # 2. Check Ban Status
        if db_user.is_banned:
            # If it's a message, maybe reply? Or just ignore.
            # Ignoring is safer for spam.
            logger.warning(f"Banned user {telegram_id} tried to interact.")
            return

        # 3. Inject user into handler data
        data["user"] = db_user

        return await handler(event, data)

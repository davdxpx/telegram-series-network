import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.utils.logging import logger
from app.models import User, Network, Series, Season, Episode

# Import Routers
from app.webapp.routes import router as webapp_router
from app.handlers import commands, management, upload, search

# --- Bot Setup ---
# Initialize Dispatcher globally (routers need to be attached)
dp = Dispatcher()

# Include Bot Routers
dp.include_router(commands.router)
dp.include_router(management.router)
dp.include_router(upload.router)
dp.include_router(search.router)

# --- Database Setup ---
async def init_db():
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        await init_beanie(database=client.get_default_database(), document_models=[User, Network, Series, Season, Episode])
        logger.info("MongoDB Connection & Beanie Initialized Successfully")
    except Exception as e:
        logger.critical(f"Failed to initialize MongoDB: {e}")
        raise e

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting TSN Bot Application...")

    # Initialize Database
    await init_db()

    # Initialize Bot
    polling_task = None
    bot = None

    try:
        # Initialize Bot instance
        logger.info(f"Initializing Bot with token prefix: {settings.BOT_TOKEN[:5]}...")
        bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        # Verify Token by calling get_me()
        bot_info = await bot.get_me()
        logger.success(f"✅ Bot Connected: @{bot_info.username} (ID: {bot_info.id})")

        # CRITICAL: Delete any existing webhook to ensure polling works
        logger.info("Checking for existing webhooks...")
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook deleted. Starting polling...")

        # Start Polling
        logger.info("📡 Starting Polling Loop...")
        # allowed_updates=["message", "edited_message", "channel_post", "edited_channel_post", "inline_query", "callback_query"]
        polling_task = asyncio.create_task(dp.start_polling(bot))

        # Add a done callback to catch silent failures in the polling loop
        def handle_polling_error(task):
            try:
                task.result()
            except asyncio.CancelledError:
                pass # Task cancellation is normal on shutdown
            except Exception as e:
                logger.exception(f"❌ Polling Task Crashed: {e}")

        polling_task.add_done_callback(handle_polling_error)

        yield

    except Exception as e:
        logger.critical(f"❌ Critical Startup Error: {e}")
        # We yield to allow the container to stay alive (maybe for debug),
        # but functionality will be broken.
        yield

    finally:
        # Shutdown
        logger.info("🛑 Shutting down...")
        if bot and bot.session:
            await bot.session.close()
            logger.info("Bot session closed.")

        if polling_task:
            polling_task.cancel()
            try:
                await polling_task
            except asyncio.CancelledError:
                pass
            logger.info("Polling task cancelled.")

# --- FastAPI App ---
app = FastAPI(title="TSN Bot API", lifespan=lifespan)

# Mount Static Files (Frontend)
app.mount("/static", StaticFiles(directory="app/webapp/static"), name="static")

# Include WebApp/Stream Routers
app.include_router(webapp_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "TSN Bot"}

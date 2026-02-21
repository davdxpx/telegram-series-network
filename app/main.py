import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.models import AdminSettings, StorageChannel, Bundle, Series, Season, Episode, User
from app.middlewares.auth import AuthMiddleware
from app.utils.logging import logger, setup_logging

# Import Routers
from app.webapp.routes import router as webapp_router
from app.handlers import user_commands, channel_post

# --- Global Instances ---
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
mongo_client: AsyncIOMotorClient = None

# --- Database Setup ---
async def init_db():
    global mongo_client
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
        # Use explicit database name 'tsn_bot' if none is provided in the URI
        try:
            db = mongo_client.get_default_database()
        except Exception:
            logger.warning("No default database in URI, using 'tsn_bot'")
            db = mongo_client.get_database("tsn_bot")

        await init_beanie(
            database=db,
            document_models=[
                AdminSettings,
                StorageChannel,
                Bundle,
                Series,
                Season,
                Episode,
                User
            ]
        )
        logger.info("✅ MongoDB Connection & Beanie Initialized Successfully")

        # Initialize AdminSettings if not exists
        existing_settings = await AdminSettings.find_one(AdminSettings.owner_telegram_id == settings.OWNER_TELEGRAM_ID)
        if not existing_settings:
            logger.info("⚙️ Creating initial AdminSettings...")
            await AdminSettings(
                owner_telegram_id=settings.OWNER_TELEGRAM_ID,
                tmdb_api_key=settings.TMDB_API_KEY
            ).create()

    except Exception as e:
        logger.critical(f"❌ Failed to initialize MongoDB: {e}")
        raise e

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Logging
    setup_logging(level=settings.LOG_LEVEL)

    # Startup
    logger.info("🚀 Starting TSN Bot Application...")
    await init_db()

    # Register Bot Routers
    dp.include_router(user_commands.router)
    dp.include_router(channel_post.router)

    # Register Middlewares
    dp.update.middleware(AuthMiddleware())

    # Start Polling (Background Task)
    polling_task = asyncio.create_task(start_bot_polling())

    yield

    # Shutdown
    logger.info("🛑 Shutting down...")
    if polling_task:
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass

    if bot.session:
        await bot.session.close()

async def start_bot_polling():
    # Drop pending updates to avoid flooding on restart
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("📡 Starting Polling Loop...")

    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        logger.info("Polling cancelled.")
    except Exception as e:
        logger.error(f"Polling error: {e}")

# --- FastAPI App ---
app = FastAPI(title="TSN Bot API", lifespan=lifespan)

# CORS (Allow everything for local dev/WebApps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (Frontend)
app.mount("/static", StaticFiles(directory="app/webapp/static"), name="static")

# Include WebApp/Stream Routers
app.include_router(webapp_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "TSN Bot", "version": "1.0.0"}

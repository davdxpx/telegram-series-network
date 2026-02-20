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
    client = AsyncIOMotorClient(settings.MONGO_URI)
    await init_beanie(database=client.get_default_database(), document_models=[User, Network, Series, Season, Episode])
    logger.info("MongoDB Initialized")

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")

    # Initialize Database
    await init_db()

    # Initialize Bot here (inside async context) to avoid "Token is invalid" error at module import time
    # This allows the app to start even if the token is bad (it will just fail to poll, but not crash the whole container immediately if we handle it)
    try:
        bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        logger.info("Bot initialized successfully")

        # Start Bot Polling in Background
        # In production, recommend running bot and webapp as separate services or using a proper supervisor.
        # For self-hosted/docker-compose simplicity, we run them together.
        polling_task = asyncio.create_task(dp.start_polling(bot))

        yield

        # Shutdown
        logger.info("Shutting down...")
        await bot.session.close()
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        # Yielding even if bot fails allows FastAPI to still run (e.g. for health checks or static files)
        yield

# --- FastAPI App ---
app = FastAPI(title="TSN Bot API", lifespan=lifespan)

# Mount Static Files (Frontend)
app.mount("/static", StaticFiles(directory="app/webapp/static"), name="static")

# Include WebApp/Stream Routers
app.include_router(webapp_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

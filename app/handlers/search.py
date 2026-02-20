from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from app.models import Series
from app.utils.logging import logger

router = Router()

@router.inline_query()
async def inline_search(query: InlineQuery):
    text = query.query or ""

    results = []

    # Basic search in Series titles
    # In a real app we'd search episodes too and filter by user's networks
    # This requires looking up the user, finding their networks, and querying Series in those networks.

    # Mock result for now to demonstrate functionality
    if len(text) > 2:
        # Mock search: Find any series matching text
        series_list = await Series.find({"title": {"$regex": text, "$options": "i"}}).to_list()

        for s in series_list:
            results.append(
                InlineQueryResultArticle(
                    id=str(s.id),
                    title=s.title,
                    description=s.overview[:100] if s.overview else "",
                    thumbnail_url=f"https://image.tmdb.org/t/p/w200{s.poster_path}" if s.poster_path else None,
                    input_message_content=InputTextMessageContent(
                        message_text=f"🎬 **{s.title}**\n{s.overview}"
                    )
                )
            )

    await query.answer(results, cache_time=1, is_personal=True)

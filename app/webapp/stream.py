import aiohttp
from fastapi import APIRouter, HTTPException, Request, Header
from fastapi.responses import StreamingResponse
from typing import Optional
from app.config import settings
from app.utils.logging import logger

router = APIRouter()

async def get_file_path(file_id: str) -> str:
    """Fetch the file path from Telegram API using bot token."""
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getFile?file_id={file_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=404, detail="File not found on Telegram")
            data = await resp.json()
            if not data.get("ok"):
                raise HTTPException(status_code=404, detail="Telegram Error")
            return data["result"]["file_path"]

@router.get("/stream/{file_id}")
async def stream_video(
    file_id: str,
    request: Request,
    range: Optional[str] = Header(None)
):
    """
    Proxies the video stream from Telegram to the client.
    Supports Range requests for seeking.
    """
    try:
        file_path = await get_file_path(file_id)
        video_url = f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_path}"

        # Determine range headers
        headers = {}
        if range:
            headers["Range"] = range

        async def stream_generator():
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url, headers=headers) as resp:
                    # Forward status code (206 Partial Content or 200 OK)
                    # We need to manually set the status on StreamingResponse if needed,
                    # but usually it just streams the body.
                    # For correct seeking, we need to forward Content-Range, Content-Length, Accept-Ranges.

                    # Note: Forwarding headers directly can be tricky with aiohttp -> FastAPI
                    # Let's yield chunks.
                    async for chunk in resp.content.iter_chunked(1024 * 64):
                        yield chunk

        # Get initial response to set headers
        async with aiohttp.ClientSession() as session:
             # Just HEAD request or initial GET to inspect headers
            async with session.get(video_url, headers=headers) as resp:
                response_headers = {
                    "Content-Range": resp.headers.get("Content-Range"),
                    "Content-Length": resp.headers.get("Content-Length"),
                    "Accept-Ranges": "bytes",
                    "Content-Type": resp.headers.get("Content-Type", "video/mp4"),
                }
                # Filter None values
                response_headers = {k: v for k, v in response_headers.items() if v is not None}

                status_code = resp.status

        return StreamingResponse(
            stream_generator(),
            status_code=status_code,
            headers=response_headers,
            media_type="video/mp4"
        )

    except Exception as e:
        logger.error(f"Streaming error: {e}")
        raise HTTPException(status_code=500, detail="Streaming failed")

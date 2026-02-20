from guessit import guessit
from typing import Dict, Any, Optional
from app.utils.logging import logger

def parse_filename(filename: str) -> Dict[str, Any]:
    """
    Parses a filename using guessit and returns structured data.
    """
    try:
        guess = guessit(filename)

        result = {
            "title": guess.get("title"),
            "season": guess.get("season"),
            "episode": guess.get("episode"),
            "year": guess.get("year"),
            "type": guess.get("type"), # 'episode' or 'movie'
            "container": guess.get("container"),
            "mimetype": guess.get("mimetype"),
        }

        # Ensure season/episode are lists or single ints, we prefer single ints for simple logic
        # If list, take first (simplification for MVP)
        if isinstance(result["season"], list):
             result["season"] = result["season"][0]
        if isinstance(result["episode"], list):
             result["episode"] = result["episode"][0]

        logger.debug(f"Parsed '{filename}': {result}")
        return result
    except Exception as e:
        logger.error(f"Error parsing filename '{filename}': {e}")
        return {}

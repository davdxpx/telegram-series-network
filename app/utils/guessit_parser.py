from guessit import guessit
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class MediaParser:
    """
    Parses filenames to extract show info (Name, Season, Episode).
    """

    @staticmethod
    def parse_filename(filename: str) -> Dict:
        """
        Uses guessit to parse the filename.
        Returns a dictionary with normalized keys.
        """
        try:
            guess = guessit(filename)

            result = {
                "title": guess.get("title"),
                "season": guess.get("season"),
                "episode": guess.get("episode"),
                "year": guess.get("year"),
                "type": guess.get("type", "episode"), # episode or movie
                "quality": guess.get("screen_size"), # 1080p, 720p
                "source": guess.get("source"), # BluRay, Web
                "original_filename": filename
            }

            # Normalize list to single int if multiple episodes in one file (not supported well yet)
            if isinstance(result["episode"], list):
                result["episode"] = result["episode"][0]

            if isinstance(result["season"], list):
                result["season"] = result["season"][0]

            return result

        except Exception as e:
            logger.error(f"Error parsing filename '{filename}': {e}")
            return {"original_filename": filename, "error": str(e)}

    @staticmethod
    def is_video_file(filename: str) -> bool:
        """
        Simple check for video extensions.
        """
        video_extensions = ['.mkv', '.mp4', '.avi', '.mov', '.webm', '.flv']
        return any(filename.lower().endswith(ext) for ext in video_extensions)

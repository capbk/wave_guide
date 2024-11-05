from flask import abort
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

SONG_MODE = "song"
MOOD_MODE = "mood"

def validate_new_playlist_request(request_json: Dict[str, Any]) -> None:
    """Validates the request payload for creating a new playlist.
    
    Args:
        request_json: The JSON payload from the request
        
    Raises:
        werkzeug.exceptions.BadRequest: If validation fails
    """
    if not request_json or "source_mode" not in request_json:
        logger.error("request must include source_mode")
        abort(400)
    if "destination_mode" not in request_json:
        logger.error("request must include destination_mode")
        abort(400)

    source_mode = request_json["source_mode"]
    destination_mode = request_json["destination_mode"]
    if source_mode not in [SONG_MODE, MOOD_MODE] or destination_mode not in [SONG_MODE, MOOD_MODE]:
        logger.error(f"Unknown source or destination mode: {source_mode} or {destination_mode}. Must provide one of the modes 'song' or 'mood'")
        abort(400)

    if source_mode == SONG_MODE and "seed_track_id" not in request_json:
        logger.error("source mode is song but no seed_track_id requested")
        abort(400)
    if source_mode == MOOD_MODE and "source_mood" not in request_json:
        logger.error("source mode is mood but no source_mood requested")
        abort(400)
    if destination_mode == SONG_MODE and "seed_track_id" not in request_json:
        logger.error("destination mode is song but no seed_track_id requested")
        abort(400)
    if destination_mode == MOOD_MODE and "destination_mood" not in request_json:
        logger.error("destination mode is mood but no destination_mood requested")
        abort(400) 
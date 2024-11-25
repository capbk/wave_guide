import spotipy
from typing import List, Tuple
from flask import session as flask_session

from recommendation_engine.bookend_seeds_track_finder import BookendSeedsTrackFinder
from recommendation_engine.mood_track_finder import MoodTrackFinder


SONG_MODE = "song"
MOOD_MODE = "mood"

# TODO: move this to spotify service
def _create_spotify_playlist(
    sp: spotipy.Spotify, recommendation_uris: List[str], point_a_label: str, point_b_label: str
) -> Tuple[str, str]:
    user_id = sp.current_user()["id"]
    playlist_name = f"Wave Guide from {point_a_label} to {point_b_label}"
    playlist_id = sp.user_playlist_create(user_id, playlist_name, public=False)["id"]
    sp.playlist_add_items(playlist_id, recommendation_uris)
    # TODO: speficy fields=
    playlist_metadata = sp.user_playlist(user_id, playlist_id)  # , fields=["external_urls", "name", "images"])
    resp = {
        "url": playlist_metadata["external_urls"]["spotify"],
        "name": playlist_metadata["name"],
        "image": playlist_metadata["images"][0]["url"],
    }
    return resp


def create_song_to_song_playlist(sp: spotipy.Spotify, seed_track_id: str, destination_track_id: str):
    # TODO: can we get this data from the initial search to avoid this call?
    seed_track = sp.track(seed_track_id)
    destination_track = sp.track(destination_track_id)
    recommended_tracks = BookendSeedsTrackFinder(sp, seed_track, destination_track).recommend()
    # TODO: remove this extra loop
    recommendation_uris = [track["uri"] for track in recommended_tracks]
    return _create_spotify_playlist(sp, recommendation_uris, seed_track["name"], destination_track["name"])

def create_playlist(request, sp: spotipy.Spotify, session: flask_session):
    # track to start the playlist
    source_mode = request.json["source_mode"]
    source_track_id = ""
    if source_mode == SONG_MODE:
        source_track_id = request.json["seed_track_id"]
    elif source_mode == MOOD_MODE:
        track_finder = MoodTrackFinder(sp, request.json["source_mood"], 1, session)
        source_track_id = track_finder.find()[0]["id"]

    # track to end the playlist
    destination_mode = request.json["destination_mode"]
    destination_track_id = ""
    if destination_mode == SONG_MODE:
        destination_track_id = request.json["destination_track_id"]
    elif destination_mode == MOOD_MODE:
        track_finder = MoodTrackFinder(sp, request.json["destination_mood"], 2, session)
        recs = track_finder.find()
        for rec in recs:
            if rec["id"] != source_track_id:
                destination_track_id = rec["id"]
                break

    return create_song_to_song_playlist(sp, source_track_id, destination_track_id)
import spotipy
from typing import List, Tuple

from recommendation_engine.bookend_seeds_track_finder import BookendSeedsTrackFinder


def _create_playlist(
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
    recommended_tracks = []
    destination_track = sp.track(destination_track_id)
    recommended_tracks = BookendSeedsTrackFinder(sp, seed_track, destination_track).recommend()
    # TODO: remove this extra loop
    recommendation_uris = [track["uri"] for track in recommended_tracks]
    return _create_playlist(sp, recommendation_uris, seed_track["name"], destination_track["name"])

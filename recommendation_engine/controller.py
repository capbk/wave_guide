from os import getenv
from builtins import ValueError

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Dict, Tuple, Any
from statistics import median, mean

from recommendation_engine.source_track_destination_cheer import TrackToCheerRecommender
from recommendation_engine.source_track_destination_energy import TrackToEnergyRecommender
from recommendation_engine.bookend_seeds_track_finder import BookendSeedsTrackFinder
from recommendation_engine.mood_to_mood_track_finder import MoodToMoodTrackFinder

MOOD_HAPPY = "happy"
MOOD_ENERGIZED = "energized"


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
    # get metdata for track.
    # TODO: can we get this data from the initial search to avoid this call?
    # TODO: validate early
    seed_track = sp.track(seed_track_id)
    recommended_tracks = []
    destination_track = sp.track(destination_track_id)
    recommended_tracks = BookendSeedsTrackFinder(sp, seed_track, destination_track).recommend()
    # TODO: remove this extra loop
    recommendation_uris = [track["uri"] for track in recommended_tracks]
    return _create_playlist(sp, recommendation_uris, seed_track["name"], destination_track["name"])


def create_mood_to_mood_playlist(sp: spotipy.Spotify, source_mood: str, destination_mood: str):
    recommended_tracks = MoodToMoodTrackFinder(sp, source_mood, destination_mood).recommend()
    # TODO: remove this extra loop
    recommendation_uris = [track["uri"] for track in recommended_tracks]
    return _create_playlist(sp, recommendation_uris, source_mood, destination_mood)


def create_song_to_mood_playlist(sp: spotipy.Spotify, seed_track_id: str, destination_mood: str):
    seed_track = sp.track(seed_track_id)
    recommendation_uris = _get_song_to_mood_tracks(sp, seed_track, destination_mood)
    return _create_playlist(sp, recommendation_uris, seed_track["name"], destination_mood)


def create_mood_to_song_playlist(sp: spotipy.Spotify, source_mood: str, destination_track_id: str):
    destination_track = sp.track(destination_track_id)
    recommendation_uris = _get_song_to_mood_tracks(sp, destination_track, source_mood)
    recommendation_uris.reverse()
    return _create_playlist(sp, recommendation_uris, source_mood, destination_track["name"])

# TODO: remove in refactor
def _get_song_to_mood_tracks(sp: spotipy.Spotify, seed_track: Dict[str, Any], destination_mood: str):
    num_tracks = 5
    # get metdata for track.
    # TODO: can we get this data from the initial search to avoid this call?
    cleaned_mood = destination_mood.lower()
    recommended_tracks = []
    if cleaned_mood == MOOD_ENERGIZED:
        recommended_tracks = TrackToEnergyRecommender(sp, seed_track, num_tracks).recommend()
    # default to cheer up mood
    elif cleaned_mood == MOOD_HAPPY:
        recommended_tracks = TrackToCheerRecommender(sp, seed_track, num_tracks).recommend()
    else:
        raise ValueError(
            f"Unknown mood: {destination_mood} provided. Must provide one of the moods 'happy' or 'energized'"
        )
    # TODO: remove this extra loop
    return [track["uri"] for track in recommended_tracks]


if __name__ == "__main__":
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=getenv("SPOTIPY_CLIENT_ID"),
            client_secret=getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=getenv("SPOTIPY_REDIRECT_URI"),
            scope="user-library-read user-top-read playlist-modify-private",
            open_browser=False,
        )
    )
    print(create_song_to_song_playlist(sp, "30HCB1FoE77IfGRyNv4eFq", "0v7s87oLwbYYIm3TF8WwoZ"))
    # print(create_playlist(sp, "30HCB1FoE77IfGRyNv4eFq", "happy"))

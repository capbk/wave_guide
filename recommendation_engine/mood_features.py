import spotipy
from typing import Dict, List
from statistics import median, mean


def fetch_top_tracks_features(sp: spotipy.Spotify, num_tracks: int) -> List[Dict[str, float]]:
    print("fetching top tracks to analyze preferences")
    # TODO: experiment with time_range
    # TODO: cache this in a multi tenant safe way
    top_tracks = sp.current_user_top_tracks(limit=num_tracks, time_range="medium_term")  # 50 is max limit
    if top_tracks["total"] == 0:
        return []
    top_track_ids = [item["id"] for item in top_tracks["items"]]
    return sp.audio_features(top_track_ids), top_track_ids


def get_cheer_up_features(top_tracks_features: List[Dict[str, float]]) -> Dict[str, float]:
    if len(top_tracks_features) == 0:
        # TODO: experiment with defaults.
        return {"valence": 1, "danceability": 0.6, "energy": 0.6}

    our_features = ["valence", "danceability", "energy"]
    cheer_up_features = {}

    # TODO: reduce time complexity without adding too much readability complexity
    for feature in our_features:
        values = [track[feature] for track in top_tracks_features]
        cheer_up_features[feature] = max(values)
        if feature == "energy":
            cheer_up_features[feature] = median(values)

    cheer_up_features["valence"] = cheer_up_features["valence"] * 1.4
    cheer_up_features["danceability"] = cheer_up_features["danceability"] * 1.25

    return cheer_up_features


def get_energize_features(top_tracks_features: List[Dict[str, float]]) -> Dict[str, float]:
    if len(top_tracks_features) == 0:
        # TODO: experiment with defaults.
        return {"valence": 0.8, "danceability": 0.8, "energy": 1}

    our_features = ["valence", "danceability", "energy"]
    destination_features = {}

    # TODO: reduce time complexity without adding too much readability complexity
    for feature in our_features:
        values = [track[feature] for track in top_tracks_features]
        destination_features[feature] = max(values)

    destination_features["valence"] = destination_features["valence"] * 1.4
    destination_features["danceability"] = destination_features["danceability"] * 1.4

    return destination_features

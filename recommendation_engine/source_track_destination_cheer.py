from dataclasses import dataclass
import spotipy
from typing import Dict, Any
from recommendation_engine.single_seed_track_finder import SingleSeedTrackFinder
from statistics import median


@dataclass
class TrackToCheerRecommender:
    """gets a list of tracks starting with a seed track
    and moving towards the Cheer Mood
    """

    sp: spotipy.Spotify
    seed_track: Dict[str, Any]
    num_tracks: int

    def __init__(self, sp: spotipy.Spotify, seed_track: Dict[str, Any], num_tracks: int):
        self.sp = sp
        self.seed_track = seed_track
        self.num_tracks = num_tracks

    def recommend(self):
        finder = SingleSeedTrackFinder(
            sp=self.sp,
            seed_track=self.seed_track,
            num_tracks=self.num_tracks,
            source_features=self.sp.audio_features([self.seed_track["id"]])[0],
            destination_features=self.fetch_destination_features(),
            acceleration_factor=0.7,
            target_min_multiplier={"valence": 0.6},
        )
        return finder.recommend()

    def fetch_destination_features(self) -> Dict[str, float]:
        print("fetching top tracks to analyze preferences")
        # TODO: experiment with time_range
        # TODO: cache this in a multi tenant safe way
        top_tracks = self.sp.current_user_top_tracks(limit=20, time_range="medium_term")  # 50 is max limit
        if top_tracks["total"] == 0:
            # TODO: experiment with defaults.
            return {"valence": 1, "danceability": 0.6, "energy": 0.6}
        top_track_ids = [item["id"] for item in top_tracks["items"]]
        top_tracks_features = self.sp.audio_features(top_track_ids)
        our_features = ["valence", "danceability", "energy"]

        destination_features = {}

        # TODO: reduce time complexity without adding too much readability complexity
        for feature in our_features:
            values = [track[feature] for track in top_tracks_features]
            destination_features[feature] = max(values)
            if feature == "energy":
                destination_features[feature] = median(values)

        destination_features["valence"] = destination_features["valence"] * 1.4
        destination_features["danceability"] = destination_features["danceability"] * 1.25

        return destination_features

from dataclasses import dataclass
import spotipy
from typing import Dict, Any, Optional, List, Tuple
import pprint
from recommendation_engine import mood_features

COUNTRY = "US"  # TODO: get this from user metadata
MOOD_HAPPY = "happy"
MOOD_ENERGIZED = "energized"

# TODO: is this a valid use of dataclass
@dataclass
class MoodToMoodTrackFinder:
    """Core recommendaiton function of app.
    Takes in starting and ending moods
    then creates a list of tracks"""

    sp: spotipy.Spotify
    source_mood: str  # acceptable mood string cheer_up or energize
    destination_mood: str  # acceptable mood string cheer_up or energize

    # target_min_multiplier defines how much we will allow the min features to dip below the target
    # for each call to the recommend endpoint
    # 1 sets the target as min,
    # 0 or missing feature key will not set a minimum
    target_min_multiplier: Optional[Dict[str, float]] = None
    # target_max_multiplier defines how much we will allow the max features to go above the target
    # for each call to the recommend endpoint
    # 1 sets the target as max,
    # 0 or missing feature key will not set a maximum
    # 2, for example, would set double the target as the max
    target_max_multiplier: Optional[Dict[str, float]] = None

    def __init__(
        self,
        sp: spotipy.Spotify,
        source_mood: str,
        destination_mood: str,
        # TODO: maybe abstract this inside of the actual
        # class since this one is not used by other recommenders
        target_min_multiplier: Optional[Dict[str, float]] = None,
        target_max_multipler: Optional[Dict[str, float]] = None,
    ):
        self.sp = sp
        self.source_mood = source_mood.lower()
        self.destination_mood = destination_mood.lower()
        self.target_min_multiplier = target_min_multiplier
        self.target_max_multipler = target_max_multipler
        self.num_tracks = 5
        self.acceleration_factor = 1
        self.seed_top_tracks = []

    def recommend(self):
        self.set_endpoints_features()
        return self.find_tracks()

    def set_endpoints_features(self):
        top_tracks_features, top_track_ids = mood_features.fetch_top_tracks_features(self.sp, self.num_tracks)
        self.seed_top_tracks = top_track_ids[:4]
        mood_handlers = {
            MOOD_HAPPY: mood_features.get_cheer_up_features,
            MOOD_ENERGIZED: mood_features.get_energize_features,
        }
        source_features = mood_handlers[self.source_mood](top_tracks_features)
        self.source_features = source_features

        destination_features = source_features
        if self.destination_mood != self.source_mood:
            destination_features = mood_handlers[self.destination_mood](top_tracks_features)
        self.destination_features = destination_features

    @staticmethod
    def build_kwargs_from_features(
        source_features: Dict[str, float],
        destination_features: Dict[str, float],
        step_size: int,
        target_min_multiplier: Dict[str, float],
        target_max_multiplier: Dict[str, float],
    ) -> Tuple[Dict[str, float]]:
        recommendation_kwargs = {}
        updated_source_features = {}
        for feature in source_features:
            target_key = f"target_{feature}"
            # use max 0 to prevent moving back in the other direction
            target = source_features[feature] + max(
                0, (destination_features[feature] - source_features[feature]) / step_size
            )
            recommendation_kwargs[target_key] = target
            updated_source_features[feature] = target
            if target_min_multiplier is not None:
                min_key = f"min_{feature}"
                min_feature = target * target_min_multiplier.get(feature, 0)
                recommendation_kwargs[min_key] = min_feature

            if target_max_multiplier is not None and target_max_multiplier.get(feature, 0) != 0:
                max_key = f"max_{feature}"
                max_feature = target * target_max_multiplier
                recommendation_kwargs[max_key] = max_feature
        return updated_source_features, recommendation_kwargs

    # TODO: break into helper functions for readability
    def find_tracks(self):
        source_features = self.source_features
        destination_features = self.destination_features

        pp = pprint.PrettyPrinter(indent=4, width=120)

        playlist_tracks = []
        track_names = []
        artist_ids = []
        seed_tracks = self.seed_top_tracks
        # if not seed_tracks:
        # TODO: fetch 5 random genres for users who have no spotify history

        recommendation_pool_size = 3
        step_size = self.num_tracks
        for i in range(self.num_tracks):
            source_features, recommendation_kwargs = self.build_kwargs_from_features(
                source_features, destination_features, step_size, self.target_min_multiplier, self.target_max_multiplier
            )
            print("getting recommendations using targets")
            pp.pprint(recommendation_kwargs)
            recs = self.sp.recommendations(
                limit=recommendation_pool_size, seed_tracks=seed_tracks, country=COUNTRY, **recommendation_kwargs,
            )

            print("recommendations for seeds", track_names)
            pp.pprint([f"{rec['name']} - {rec['artists'][0]['name']}" for rec in recs["tracks"]])
            print("\n")

            # prevent duplicates of the same songs or artists
            # if they are all duplicates it will stick with the first recommendation
            # TODO: handle tracks with multiple artists?
            # TODO: break out into helper?
            next_track = recs["tracks"][0]
            for recommended_track in recs["tracks"]:
                recommended_track_name = recommended_track["name"].lower()
                recommended_track_artist_id = recommended_track["artists"][0]["id"]
                if recommended_track_name in track_names or recommended_track_artist_id in artist_ids:
                    continue
                next_track = recommended_track
                track_names.append(recommended_track_name)
                artist_ids.append(recommended_track_artist_id)
                break

            playlist_tracks.append(next_track)
            # TODO: is there a cleaner way to only use the top tracks for the first recommendation?
            if seed_tracks == self.seed_top_tracks:
                seed_tracks = []
            seed_tracks.append(next_track["id"])
            step_size = step_size * self.acceleration_factor

        return playlist_tracks

from numpy import percentile
import pprint
from random import choices
import spotipy
from statistics import median
from typing import Dict

# TODO: make global?
MOOD_HAPPY = "happy"
MOOD_ENERGIZED = "energized"
MOOD_CALM = "calm"
# MOOD_SAD = "sad"
# MOOD_ANGRY = "angry"
SUPPORTED_MOODS = [MOOD_HAPPY, MOOD_ENERGIZED, MOOD_CALM]
COUNTRY = "US"  # TODO: get this from user metadata


class MoodTrackFinder:
    def __init__(self, sp: spotipy.Spotify, mood:str, num_tracks: int):
        mood = mood.lower()
        if mood not in SUPPORTED_MOODS:
            raise ValueError(
                f"Unknown mood: {mood} provided. Supported moods include {SUPPORTED_MOODS}"
            )
        if num_tracks < 1:
            # TODO: is this the right error to return?
            raise ValueError("find_tracks_for_mood requires num_tracks greater than 0")

        self.sp = sp
        self.mood = mood
        self.num_tracks = num_tracks

    def find(self):
        """
        returns a list of tracks from spotify reccomendations response
        https://developer.spotify.com/documentation/web-api/reference/get-recommendations
        """
        # TODO: experiment with time_range
        # TODO: experiment with randomness when grabbing 5 top tracks
        # TODO: experiment with including override seed track ids to make resulting playlist more cohesive
        # TODO: cache this in a multi tenant safe way
        print("fetching top tracks to analyze preferences")
        top_tracks = self.sp.current_user_top_tracks(limit=50, time_range="long_term")  # 50 is max limit
        top_track_ids = []
        top_tracks_features = None
        if top_tracks["total"] != 0:
            top_track_ids = [item["id"] for item in top_tracks["items"]]
            top_tracks_features = self.sp.audio_features(top_track_ids)

        # get personalized features for corresponding mood
        user_features = {}
        if self.mood == MOOD_HAPPY:
            user_features = self.create_happy_features(top_tracks_features)
        elif self.mood == MOOD_ENERGIZED:
            user_features = self.create_energized_features(top_tracks_features)
        elif self.mood == MOOD_CALM:
            user_features = self.create_calm_features(top_tracks_features)

        # get tracks
        recommendation_kwargs = {}
        for feature in user_features:
            recommendations_request_key = f"target_{feature}"
            recommendation_kwargs[recommendations_request_key] = user_features[feature]

        randomized_seed_tracks = choices(top_track_ids, k=5)
        recs = self.sp.recommendations(
            limit=self.num_tracks, seed_tracks=randomized_seed_tracks, country=COUNTRY, **recommendation_kwargs,
        )
        print("recommendations from spotify API")
        pprint.PrettyPrinter(indent=4, width=120).pprint(recs["tracks"])
        return recs["tracks"]

    @staticmethod
    def create_happy_features(top_tracks_features) -> Dict[str, float]:
        """
        Uses the user's top tracks, when available, to derive 'happy' track features
        that will fit their tastes
        """
        # TODO: experiment with defaults.
        default_features = {"valence": 1, "danceability": 0.6, "energy": 0.6}
        if top_tracks_features == {} or top_tracks_features is None:
            return default_features

        our_features = ["valence", "danceability", "energy"]
        happy_features = {}

        # TODO: reduce time complexity without adding too much readability complexity
        # take the max valence and danceability.  Take the median energy
        # TODO: max danceability may not be ideal
        for feature in our_features:
            # get all feature values across top tracks
            values = [track[feature] for track in top_tracks_features]
            happy_features[feature] = max(values)
            if feature == "energy":
                happy_features[feature] = median(values)

        # boost even higher
        # happy_features["valence"] = track["valence"] * 1.4
        # happy_features["danceability"] = happy_features["danceability"] * 1.25
        print("personalized happy_features ", happy_features)
        return happy_features

    @staticmethod
    def create_energized_features(top_tracks_features) -> Dict[str, float]:
        default_features = {"valence": 0.8, "danceability": 0.8, "energy": 1}
        if top_tracks_features == {} or top_tracks_features is None:
            return default_features

        energized_features = {}

        # max valence
        valence_values = [track["valence"] for track in top_tracks_features]
        energized_features["valence"] = max(valence_values)
        # max danceability
        danceability_values = [track["danceability"] for track in top_tracks_features]
        energized_features["danceability"] = max([max(danceability_values), 0.7])
        # min energy with a cieling of 0.3
        energy_values = [track["energy"] for track in top_tracks_features]
        energized_features["energy"] = max([max(energy_values), 0.7])

        print("personalized energized features", energized_features)
        return energized_features

    @staticmethod
    def create_calm_features(top_tracks_features) -> Dict[str, float]:
        default_features = {"valence": 0.6, "danceability": 0.1, "energy": 0.25, "acousticness": 0.75}
        if top_tracks_features == {} or top_tracks_features is None:
            return default_features

        calm_features = {}

        # median valence
        valence_values = [track["valence"] for track in top_tracks_features]
        calm_features["valence"] = max([percentile(valence_values, 0.7), 0.5])
        # min danceability
        danceability_values = [track["danceability"] for track in top_tracks_features]
        calm_features["danceability"] = min([min(danceability_values), 0.4])
        # min energy with a cieling of 0.3
        energy_values = [track["energy"] for track in top_tracks_features]
        calm_features["energy"] = min([percentile(energy_values, 0.25), 0.25])
        # 75th percentile acousticness
        acousticness_values = [track["acousticness"] for track in top_tracks_features]
        calm_features["acousticness"] = max([percentile(acousticness_values, 75), 0.7])
        print("personalized calm features", calm_features)

        return calm_features

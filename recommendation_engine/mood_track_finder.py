import spotipy
from typing import Dict, Any, Optional, List
import pprint


# TODO: make global?
MOOD_HAPPY = "happy"
MOOD_ENERGIZED = "energized"
SUPPORTED_MOODS = [MOOD_HAPPY, MOOD_ENERGIZED]
COUNTRY = "US"  # TODO: get this from user metadata



class MoodTrackFinder:
    def __init__(self, sp: spotipy.Spotify, mood:str, num_tracks: int):
        if mood not in SUPPORTED_MOODS:
            raise ValueError(
                f"Unknown mood: {mood} provided. Supported moods include {SUPPORTED_MOODS}"
            )
        if num_tracks < 1:
            # TODO: is this the right error to return?
            raise ValueError("find_tracks_for_mood requires num_trakcks greater than 0")

        self.sp = sp
        self.mood = mood.lower()
        self.num_tracks = num_tracks

    def find(self) -> Dict[str: Any]:
        """
        returns a list of tracks from spotify reccomendations response
        https://developer.spotify.com/documentation/web-api/reference/get-recommendations
        """
        # TODO: experiment with time_range
        # TODO: cache this in a multi tenant safe way
        print("fetching top tracks to analyze preferences")
        top_tracks = self.sp.current_user_top_tracks(limit=20, time_range="medium_term")  # 50 is max limit
        top_track_ids = []
        top_tracks_features = None
        if top_tracks["total"] != 0:
            top_track_ids = [item["id"] for item in top_tracks["items"]]
            top_tracks_features = self.sp.audio_features(top_track_ids)

        # get personalized features for corresponding mood
        user_features = {}
        if self.mood == MOOD_HAPPY:
            user_features = self.create_happy_features(top_tracks_features)
        if self.mood == MOOD_ENERGIZED:
            raise ValueError("not implemented for energized yet")

        # get tracks
        recommendation_kwargs = {}
        for feature in user_features:
            recommendations_request_key = f"target_{feature}"
            recommendation_kwargs[recommendations_request_key] = user_features[feature]
        recs = self.sp.recommendations(
            limit=self.num_tracks, seed_tracks=top_track_ids[:5], country=COUNTRY, **recommendation_kwargs,
        )
        print("recommendations from spotify API")
        pp.pprint(recs["tracks"])
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
        for feature in our_features:
            # get all feature values across top tracks
            values = [track[feature] for track in top_tracks_features]
            happy_features[feature] = max(values)
            if feature == "energy":
                happy_features[feature] = median(values)

        # boost even higher
        # happy_features["valence"] = track["valence"] * 1.4
        # happy_features["danceability"] = happy_features["danceability"] * 1.25

        return happy_features

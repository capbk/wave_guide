from numpy import percentile
import pprint
from random import choices
import spotipy
from statistics import median
from typing import Dict
from werkzeug.exceptions import abort


# TODO: make global?
MOOD_HAPPY = "happy"
MOOD_ENERGIZED = "energized"
MOOD_CALM = "calm"
# MOOD_SAD = "sad"
# MOOD_ANGRY = "angry"
SUPPORTED_MOODS = [MOOD_HAPPY, MOOD_ENERGIZED, MOOD_CALM]
MARKET = "US"  # TODO: get this from user metadata


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
        # TODO: experiment with including override seed track ids to make resulting playlist more cohesive
        # TODO: cache this in a multi tenant safe way

        top_tracks = []
        top_tracks_features = None

        print("fetching top tracks to analyze preferences")
        top_tracks_resp = self.sp.current_user_top_tracks(limit=50, time_range="long_term")  # 50 is max limit
        if top_tracks_resp["total"] != 0:
            top_tracks = top_tracks_resp["items"]

            top_tracks_page_2_resp = self.sp.current_user_top_tracks(limit=50, offset=51, time_range="long_term")  # 50 is max limit
            if top_tracks_page_2_resp["total"] != 0:
                top_tracks.extend(top_tracks_page_2_resp["items"])
            top_track_ids = [track["id"] for track in top_tracks]
            top_tracks_features = self.sp.audio_features(top_track_ids)

        ################################
        ################################
        # TOGGLE PERSONALIZED TRACK FEATURES
        personalize_features = True

        # get features for corresponding mood
        user_features = {}
        if self.mood == MOOD_HAPPY:
            user_features = self.create_happy_features(top_tracks_features, personalize_features)
        elif self.mood == MOOD_ENERGIZED:
            user_features = self.create_energized_features(top_tracks_features, personalize_features)
        elif self.mood == MOOD_CALM:
            user_features = self.create_calm_features(top_tracks_features, personalize_features)

        print("user features for mood", self.mood)
        pprint.PrettyPrinter(indent=4, width=120).pprint(user_features)
        # get tracks
        randomized_seed_tracks = []
        if top_tracks:
            # can provide max of 5 seed tracks to spotify API
            randomized_seed_tracks = choices(top_tracks, k=5)
            seed_track_ids = [track["id"] for track in randomized_seed_tracks]

            print("random 5 seed tracks from user_top_tracks", [track["name"] for track in randomized_seed_tracks])
        recs = self.sp.recommendations(
            limit=self.num_tracks, seed_tracks=seed_track_ids, country=COUNTRY, **user_features,
        )
        # print("recommendations from spotify API")
        # pprint.PrettyPrinter(indent=4, width=120).pprint(recs["tracks"])
        return recs["tracks"]

    """
    Mood specific feature creation below
    each function is responsible for a specific mood's track features
    It returns a dict of kwargs that can be plugged directly into the sp.recommendations()
    function as the last argument.
    https://developer.spotify.com/documentation/web-api/reference/get-recommendations
    """

    @staticmethod
    def create_happy_features(top_tracks_features, personalize: bool) -> Dict[str, float]:
        """
        Uses the user's top tracks, when available, to derive 'happy' track features
        that will fit their tastes
        """
        # TODO: experiment with defaults.
        user_features = {
            "target_acousticness": 0.35,  # experimental
            "target_instrumentalness": 0.2,  # experimental
            "target_valence": 1,
            "target_danceability": 0.7,
            "target_energy": 0.65,
        }
        if not personalize or not top_tracks_features:
            return user_features

        # max valence
        valence_values = [track["valence"] for track in top_tracks_features]
        user_features["target_valence"] = max(valence_values)
        # max danceability
        # TODO: max danceability may not be ideal
        danceability_values = [track["danceability"] for track in top_tracks_features]
        user_features["target_danceability"] = max(danceability_values)
        # median energy
        energy_values = [track["energy"] for track in top_tracks_features]
        user_features["target_energy"] = median(energy_values)

        return user_features

    @staticmethod
    def create_energized_features(top_tracks_features, personalize: bool) -> Dict[str, float]:
        user_features = {
            "target_energy": 1,
            "target_danceability": 0.85,
            "target_valence": 0.8,
            "target_acousticness": 0.25
        }

        if not personalize or not top_tracks_features:
            return user_features

        # max valence
        valence_values = [track["valence"] for track in top_tracks_features]
        user_features["target_valence"] = max(valence_values)
        # max danceability
        danceability_values = [track["danceability"] for track in top_tracks_features]
        user_features["target_danceability"] = max([max(danceability_values), 0.7])
        # min energy with a cieling of 0.3
        energy_values = [track["energy"] for track in top_tracks_features]
        user_features["target_energy"] = max([max(energy_values), 0.7])

        return user_features

    @staticmethod
    def create_calm_features(top_tracks_features, personalize: bool) -> Dict[str, float]:
        user_features = {
            # acousticness
            "target_acousticness": 0.75,
            # danceability
            "target_danceability": 0.25,
            # energy
            "target_energy": 0.25,
            "max_energy": 0.6,
            # instrumentalness
            # "target_instrumentalness": 0.75,
            # valence
            "target_valence": 0.7,
            "min_valence": 0.53,
        }

        if not personalize or not top_tracks_features:
            return user_features

        # valence on the upper side of user tastes
        valence_values = [track["valence"] for track in top_tracks_features]
        target_valence = percentile(valence_values, 0.7)
        if target_valence >= user_features["min_valence"]:
            user_features["target_valence"] = target_valence
        # min danceability
        danceability_values = [track["danceability"] for track in top_tracks_features]
        user_features["target_danceability"] = min(danceability_values)

        # energy on lower side of tastes
        energy_values = [track["energy"] for track in top_tracks_features]
        target_energy = percentile(energy_values, 0.25)
        if target_energy <= user_features["max_energy"]:
            user_features["target_energy"] = target_energy
        # 75th percentile acousticness
        acousticness_values = [track["acousticness"] for track in top_tracks_features]
        user_features["target_acousticness"] = percentile(acousticness_values, 75)

        return user_features

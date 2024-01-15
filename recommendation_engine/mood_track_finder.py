from numpy import percentile
import pprint
from random import sample
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
COUNTRY = "US"  # TODO: get this from user metadata


class MoodTrackFinder:
    def __init__(self, sp: spotipy.Spotify, mood:str, num_tracks: int, personalize_features: bool = True):
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
        self.personalize_features = personalize_features
        self.top_tracks = self.get_top_tracks()

    def get_top_tracks(self):
        print("fetching top tracks to analyze preferences")
        top_tracks_resp = self.sp.current_user_top_tracks(limit=50, time_range="short_term")  # 50 is max limit
        # TODO: handle brand new users who have no top tracks
        # I think spotify API needs at least one seed
        if top_tracks_resp and top_tracks_resp["total"] != 0:
            return top_tracks_resp["items"]
        return []

    def find(self):
        """
        returns a list of tracks from spotify reccomendations response
        https://developer.spotify.com/documentation/web-api/reference/get-recommendations
        """

        # TODO: handle brand new users who have no top tracks
        # I think spotify API needs at least one seed
        top_artists = {}
        top_track_ids = []
        # use dict to store deduplicated ids and names. names are useful in logs for tuning algo
        for track in self.top_tracks:
            top_track_ids.append(track["id"])
            for artist in track["artists"]:
                top_artists[artist["id"]] = artist["name"]

        top_tracks_features = None
        ################################
        ################################
        # TOGGLE PERSONALIZED TRACK FEATURES
        if self.personalize_features:
            top_tracks_features = self.sp.audio_features(top_track_ids)

        # get features for corresponding mood
        mood_features = {}
        if self.mood == MOOD_HAPPY:
            mood_features = self.create_happy_features(top_tracks_features, self.personalize_features)
        elif self.mood == MOOD_ENERGIZED:
            mood_features = self.create_energized_features(top_tracks_features, self.personalize_features)
        elif self.mood == MOOD_CALM:
            mood_features = self.create_calm_features(top_tracks_features, self.personalize_features)

        # print("user features for mood", self.mood)
        # pprint.PrettyPrinter(indent=4, width=120).pprint(mood_features)
        # get tracks

        # HARD CODING TO REDUCE TESTING VARIABLES
        randomized_seed_artists = []
        if top_artists:
            # can provide max of 5 seed tracks to spotify API
            randomized_seed_artists = sample(list(top_artists.keys()), k=5)
            print("random 5 seed artists", [top_artists[artist_id] for artist_id in randomized_seed_artists])
        recs = self.sp.recommendations(
            limit=self.num_tracks, seed_artists=randomized_seed_artists, country=COUNTRY, **mood_features,
        )
        # print("recommendations from spotify API for mood", self.mood)
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
        mood_features = {
            "target_acousticness": 0.35,  # experimental
            "target_instrumentalness": 0.2,  # experimental
            "target_valence": 1,
            "target_danceability": 0.7,
            "target_energy": 0.65,
        }
        if not personalize or not top_tracks_features:
            return mood_features

        # max valence
        valence_values = [track["valence"] for track in top_tracks_features]
        mood_features["target_valence"] = max(valence_values)
        # max danceability
        # TODO: max danceability may not be ideal
        danceability_values = [track["danceability"] for track in top_tracks_features]
        mood_features["target_danceability"] = max(danceability_values)
        # median energy
        energy_values = [track["energy"] for track in top_tracks_features]
        mood_features["target_energy"] = median(energy_values)

        return mood_features

    @staticmethod
    def create_energized_features(top_tracks_features, personalize: bool) -> Dict[str, float]:
        mood_features = {
            "target_energy": 1,
            "target_danceability": 0.85,
            "target_valence": 0.8,
            "target_acousticness": 0.25
        }

        if not personalize or not top_tracks_features:
            return mood_features

        # max valence
        valence_values = [track["valence"] for track in top_tracks_features]
        mood_features["target_valence"] = max(valence_values)
        # max danceability
        danceability_values = [track["danceability"] for track in top_tracks_features]
        mood_features["target_danceability"] = max([max(danceability_values), 0.7])
        # min energy with a cieling of 0.3
        energy_values = [track["energy"] for track in top_tracks_features]
        mood_features["target_energy"] = max([max(energy_values), 0.7])

        return mood_features

    @staticmethod
    def create_calm_features(top_tracks_features, personalize: bool) -> Dict[str, float]:
        mood_features = {
            # "target_acousticness": 0.75,
            # "target_instrumentalness": 0.75,
            "target_danceability": 0.27,
            "target_energy": 0.05,
            "max_energy": 0.5,  # use min/max sparingly. see Notes folder
            "target_valence": 0.9,
        }

        if not personalize or not top_tracks_features:
            return mood_features

        # valence on the upper side of user tastes
        valence_values = [track["valence"] for track in top_tracks_features]
        target_valence = percentile(valence_values, 0.7)
        mood_features["target_valence"] = target_valence
        # min danceability
        danceability_values = [track["danceability"] for track in top_tracks_features]
        mood_features["target_danceability"] = min(danceability_values)

        # energy on lower side of tastes
        energy_values = [track["energy"] for track in top_tracks_features]
        target_energy = percentile(energy_values, 0.25)
        mood_features["target_energy"] = target_energy
        # 75th percentile acousticness
        acousticness_values = [track["acousticness"] for track in top_tracks_features]
        mood_features["target_acousticness"] = percentile(acousticness_values, 75)

        return mood_features

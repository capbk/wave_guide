import pprint
from random import sample
import spotipy
from statistics import median
from typing import Dict, List
from werkzeug.exceptions import abort


# TODO: make global?
MOOD_HAPPY = "happy"
MOOD_ENERGIZED = "energized"
MOOD_CALM = "calm"
# MOOD_SAD = "sad"
# MOOD_ANGRY = "angry"
SUPPORTED_MOODS = [MOOD_HAPPY, MOOD_ENERGIZED, MOOD_CALM]
COUNTRY = "US"  # TODO: get this from user metadata

# available genres: https://developer.spotify.com/documentation/web-api/reference/get-recommendation-genres
# can provide max of 5 seeds (combined track + artist + genre) to spotify API
mood_genres = {
    MOOD_HAPPY: ["happy", "pop", "summer"],
    MOOD_ENERGIZED: ["electronic", "dance", "work-out"],
    MOOD_CALM: ["classical", "acoustic", "chill"],
}


class MoodTrackFinder:
    def __init__(self, sp: spotipy.Spotify, mood:str, num_tracks: int, session=None):
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
        # TODO: is this ok in __init__?
        if session and "top_artists" in session:
            self.top_artists = session.get("top_artists")
        else:
            print("calling get top artists") # TODO: proper logger at debug level
            top_artists = self._get_top_artists()
            self.top_artists = top_artists
            if session:
                session["top_artists"] = top_artists

    # returns dict{time_period: [{"name": str, "id": str}]}
    def _get_top_artists(self) -> Dict[str, List[Dict[str, str]]]:
        print("fetching top artists to seed recommendations")
        artists_per_time_range = {"short_term": [], "medium_term": [], "long_term": []}
        for time_range in artists_per_time_range:
            # 50 is max limit
            top_artists_resp = self.sp.current_user_top_artists(limit=10, time_range=time_range)
            if top_artists_resp["total"] == 0:
                return artists_per_time_range
            # Only return name and id for each artist
            artists_per_time_range[time_range] = [
                {"name": artist["name"], "id": artist["id"]}
                for artist in top_artists_resp["items"]
            ]
        return artists_per_time_range

    # Fetch 5 randomized, distinct seed artists
    # 5 is the max seeds allowed
    # 2 from short term
    # 2 from medium term
    # 1 from long term
    # TODO: somehow align the artists with the mood *******
    def get_seed_artists(self):
        # de_duplicate and useful for logging
        artist_name_per_id = {}
        seed_artists = []
        args = [("short_term", 2), ("medium_term", 2), ("long_term", 1)]
        for time_range, k in args:
            time_range_artists = []
            for artist in self.top_artists[time_range]:
                artist_id = artist["id"]
                if artist_id in artist_name_per_id:
                    continue
                artist_name_per_id[artist_id] = artist["name"]
                time_range_artists.append(artist_id)
            if not time_range_artists:
                continue
            time_range_seeds = sample(time_range_artists, k)
            seed_artists.extend(time_range_seeds)
        print("seed artists for mood", self.mood, [artist_name_per_id[a_id] for a_id in seed_artists])
        return seed_artists

    def find(self):
        """
        returns a list of tracks from spotify reccomendations response
        https://developer.spotify.com/documentation/web-api/reference/get-recommendations
        """
        # get features for corresponding mood
        mood_features = {}
        if self.mood == MOOD_HAPPY:
            mood_features = self.get_happy_features()
        elif self.mood == MOOD_ENERGIZED:
            mood_features = self.get_energized_features()
        elif self.mood == MOOD_CALM:
            mood_features = self.get_calm_features()
        # print("mood features for", self.mood)
        # print(mood_features)

        # can provide max of 5 seeds (combined track + artist + genre) to spotify API
        # Use a random sample for more diverse recommendations
        seed_artists = self.get_seed_artists()
        # in case where user has no top artists, use a genre instead
        if not seed_artists:
            seed_genre = mood_genres[self.mood]
            recs = self.sp.recommendations(
                limit=self.num_tracks, seed_genres=seed_genre, country=COUNTRY, **mood_features,
            )
            return recs["tracks"]

        recs = self.sp.recommendations(
            limit=self.num_tracks, seed_artists=seed_artists, country=COUNTRY, **mood_features,
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

    use min/max sparingly as they can slim down the space to the point where you get no responses
    for a given set of seeds

    acousticness, liveness, and instrumentalness all seem to be very noisy, or low quality signals.
    """

    @staticmethod
    def get_happy_features() -> Dict[str, float]:
        return {
            "target_valence": 3,
            "min_valence": 0.8,
            "min_danceability": 0.7,
            "target_energy": 0.8,
        }

    @staticmethod
    def get_energized_features() -> Dict[str, float]:
        return {
            "target_energy": 3,
            "min_energy": 0.71,
            "target_danceability": 3,
            "min_danceability": 0.6,
            "target_valence": 0.76
        }

    @staticmethod
    def get_calm_features() -> Dict[str, float]:
        return {
            "target_danceability": 0.27,
            "target_energy": 0.05,
            "max_energy": 0.5,  # use min/max sparingly. see Notes folder
            "target_valence": 0.9,
        }

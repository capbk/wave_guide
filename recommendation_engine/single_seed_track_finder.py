from dataclasses import dataclass
import spotipy
from typing import Dict, Any, Optional
import pprint

COUNTRY = "US"  # TODO: get this from user metadata


@dataclass
class SingleSeedTrackFinder:
    """Core recommendaiton function of app.
    Takes in starting and ending parameters
    then creates a list of tracks"""

    sp: spotipy.Spotify
    seed_track: Dict[str, Any]  # Spotify Get Track response
    num_tracks: int
    source_features: Dict[str, float]
    target_features: Dict[str, float]
    # acceleration_factor is a non-zero value less than or equal to 1
    # a value of 1 will lead to each target feature incrementing evenly between recommendation batches
    # shrinking the value will lead to each sequential batch making a bigger jump for target features
    # multiplying it by the denominator of 1/num_songs_to_recommend
    acceleration_factor: float = 1
    # target_min_multiplier definesv how much we will allow the min features to dip below the target
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
        seed_track: Dict[str, Any],
        num_tracks: int,
        source_features: Dict[str, float],
        destination_features: Dict[str, float],
        acceleration_factor: float = 1,
        target_min_multiplier: Optional[Dict[str, float]] = None,
        target_max_multipler: Optional[Dict[str, float]] = None,
    ):
        self.sp = sp
        self.seed_track = seed_track
        self.num_tracks = num_tracks
        self.acceleration_factor = acceleration_factor
        self.target_min_multiplier = target_min_multiplier
        self.target_max_multipler = target_max_multipler

        # slim down to currently supported features of energy, danceability, and valence
        self.source_features = {}
        self.source_features["energy"] = source_features["energy"]
        self.source_features["danceability"] = source_features["danceability"]
        self.source_features["valence"] = source_features["valence"]

        self.destination_features = {}
        self.destination_features["energy"] = destination_features["energy"]
        self.destination_features["danceability"] = destination_features["danceability"]
        self.destination_features["valence"] = destination_features["valence"]

    # TODO: break into helper functions for readability
    def recommend(self):
        pp = pprint.PrettyPrinter(indent=4, width=120)
        # tracks that will be returned from the function
        playlist_tracks = [self.seed_track]
        # keep track of names of songs to prevent a playlist full of remakes
        track_names = [self.seed_track["name"].lower()]
        # TODO: handle multiple artists for more diveserity?
        # keep track of artists to prevent duplicates for more diversity
        artist_ids = [self.seed_track["artists"][0]["id"]]
        # TODO: experiment with adding/not adding more seed tracks as you go
        # tracks that are fed into the recommend endpoint
        seed_tracks = [self.seed_track["id"]]
        source_features = self.source_features
        destination_features = self.destination_features

        recommendation_pool_size = 4
        step_size = self.num_tracks
        for i in range(self.num_tracks):
            recommendation_kwargs = {}
            for feature in source_features:
                target_key = f"target_{feature}"
                # use max 0 to prevent moving back in the other direction
                target = source_features[feature] + max(
                    0, (destination_features[feature] - source_features[feature]) / step_size
                )
                source_features[feature] = target
                recommendation_kwargs[target_key] = target

                if self.target_min_multiplier is not None:
                    min_key = f"min_{feature}"
                    min_feature = target * self.target_min_multiplier.get(feature, 0)
                    recommendation_kwargs[min_key] = min_feature

                if self.target_max_multiplier is not None and self.target_max_multiplier.get(feature, 0) != 0:
                    max_key = f"max_{feature}"
                    max_feature = target * self.target_max_multiplier
                    recommendation_kwargs[max_key] = max_feature

            print("getting recommendations using targets")
            pp.pprint(recommendation_kwargs)
            recs = self.sp.recommendations(
                limit=recommendation_pool_size, seed_tracks=seed_tracks, country=COUNTRY, **recommendation_kwargs,
            )

            print("recommendations for seeds", track_names)
            pp.pprint([f"{rec['name']} - {rec['artists'][0]['name']}" for rec in recs["tracks"]])
            print("\n")

            # recs_ids = [track["id"] for track in recs["tracks"]]
            # print("getting features for batch of recommendations with IDs", recs_ids, "\n")
            # recs_features = sp.audio_features(recs_ids)
            # pp.pprint(recs_features)

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
            seed_tracks.append(next_track["id"])
            step_size = step_size * self.acceleration_factor

        # print("\n\nrecommendation features\n")
        # recommendation_features = sp.audio_features(seed_tracks)
        # fetures_we_care_about = [
        #     {
        #         "valence": rec["valence"],
        #         "danceability": rec["danceability"],
        #         "energy": rec["energy"],
        #         "tempo": rec["tempo"],
        #     }
        #     for rec in recommendation_features
        # ]
        # pp.pprint(fetures_we_care_about)

        return playlist_tracks

import spotipy
import app_env  # not stored in git
from time import sleep
import pandas as pd
import matplotlib.pyplot as plt
from typing import List


class UserTopItems:
    def __init__(self, sp: spotipy.Spotify, time_ranges: List[str], limit: int = 50):
        if  not time_ranges:
            raise ValueError("time_ranges must be an array containing any of the values short_term, medium_term, long_term")
        for time_range in time_ranges:
            if time_range not in ["short_term", "medium_term", "long_term"]:
                raise ValueError("time_ranges must be an array containing any of the values short_term, medium_term, long_term")
        self.time_ranges = time_ranges
        if not sp:
            raise ValueError("Must provide spotipy.Spotify")
        self.sp = sp
        self.limit = limit

        top_tracks = self.fetch_top_tracks()
        self.short_term_top_tracks = top_tracks.get("short_term", {})
        self.medium_term_top_tracks = top_tracks.get("medium_term", {})
        self.long_term_top_tracks = top_tracks.get("long_term", {})

    def fetch_top_tracks(self):
        top_tracks = {}
        for time_range in self.time_ranges:
            top_tracks_resp = sp.current_user_top_tracks(limit=self.limit, time_range=time_range)  # 50 is max limit
            if top_tracks_resp["total"] == 0:
                continue
            top_tracks[time_range] = top_tracks_resp["items"]
        return top_tracks


#             top_tracks_features = None
#     top_tracks_resp = None
#     top_artists = {}
#     # print("fetching top tracks to analyze preferences")
#     top_tracks_resp = sp.current_user_top_tracks(limit=50, time_range=time_range)  # 50 is max limit
#     if top_tracks_resp["total"] == 0:
#         continue
#     top_tracks = top_tracks_resp["items"]
#     # top_tracks_page_2 = sp.current_user_top_tracks(limit=50, offset=51, time_range="long_term")
#     # top_tracks.extend(top_tracks_page_2["items"])
#     top_track_ids = []
#     top_track_names = []
#     # use dict to store deduplicated ids and names. names are useful in logs for tuning algo
#     for track in top_tracks:
#         top_track_names.append(f"{track['name']} - {track['artists'][0]['name']}")
#         if track["id"] in counts:
#             counts[track["id"]] += 1
#         else:
#             counts[track["id"]] = 1
#         # top_track_ids.append(track["id"])
#         for artist in track["artists"]:
#             top_artists[artist["id"]] = artist["name"]


# # def get_user_top_items():
auth_manager = spotipy.oauth2.SpotifyOAuth(
    client_id=app_env.SPOTIPY_CLIENT_ID,
    client_secret=app_env.SPOTIPY_CLIENT_SECRET,
    redirect_uri=app_env.SPOTIPY_REDIRECT_URI,
    scope="user-library-read user-top-read playlist-modify-private",
    open_browser=False,
)
sp = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=45, retries=0)
# tracks_data = {}
# artists_data = {}
# counts = {}
# for time_range in ["short_term", "medium_term", "long_term"]:

#     top_tracks_features = None
#     top_tracks_resp = None
#     top_artists = {}
#     # print("fetching top tracks to analyze preferences")
#     top_tracks_resp = sp.current_user_top_tracks(limit=50, time_range=time_range)  # 50 is max limit
#     if top_tracks_resp["total"] == 0:
#         continue
#     top_tracks = top_tracks_resp["items"]
#     # top_tracks_page_2 = sp.current_user_top_tracks(limit=50, offset=51, time_range="long_term")
#     # top_tracks.extend(top_tracks_page_2["items"])
#     top_track_ids = []
#     top_track_names = []
#     # use dict to store deduplicated ids and names. names are useful in logs for tuning algo
#     for track in top_tracks:
#         top_track_names.append(f"{track['name']} - {track['artists'][0]['name']}")
#         if track["id"] in counts:
#             counts[track["id"]] += 1
#         else:
#             counts[track["id"]] = 1
#         # top_track_ids.append(track["id"])
#         for artist in track["artists"]:
#             top_artists[artist["id"]] = artist["name"]
#     # top_tracks_features = sp.audio_features(top_track_ids)
#     # return top_track_names, list(top_artists.keys())

#     tracks_data[time_range] = top_track_names
#     artists_data[time_range] = list(top_artists.keys())
#     sleep(5)


# #######    

# print("finished all three time ranges")
# plt.bar(counts.keys(), counts.values())
# plt.show()

# track_df = pd.DataFrame(tracks_data)
# print("Tracks")
# print(track_df.to_string(index=False))


# if __name__ == '__main__':
#     get_user_top_items()
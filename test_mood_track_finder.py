from recommendation_engine.mood_track_finder import MoodTrackFinder
import pprint
import app_env  # not stored in git
import spotipy
from time import sleep


def get_spotify():
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        client_id=app_env.SPOTIPY_CLIENT_ID,
        client_secret=app_env.SPOTIPY_CLIENT_SECRET,
        redirect_uri=app_env.SPOTIPY_REDIRECT_URI,
        scope="user-library-read user-top-read playlist-modify-private",
        open_browser=False,
    )
    return spotipy.Spotify(auth_manager=auth_manager, requests_timeout=45, retries=0)


def main():
    pp = pprint.PrettyPrinter(indent=4, width=120)
    sp = get_spotify()
    mood = "happy"
    print("mood", mood)
    # iterate to grab some different seed tracks
    mtf = MoodTrackFinder(sp, mood, 2)
    for i in range(0, 5):
        print("\n\n=======================")
        recs = mtf.find()
        track_ids = []
        tracks = {}
        for track in recs:
            track_ids.append(track["id"])
            slimmed = {
                "name": track["name"],
                # "artist": track["artists"][0]["name"],
                "link": track["external_urls"]["spotify"]
            }
            tracks[track["id"]] = slimmed

        all_track_features = sp.audio_features(track_ids)
        for features in all_track_features:
            track_id = features["id"]
            track = tracks[track_id]
            track["valence"] = features["valence"]
            track["tempo"] = features["tempo"]
            track["danceability"] = features["danceability"]
            track["energy"] = features["energy"]
            tracks[track_id] = track
        readable_tracks = list(tracks.values())
        pp.pprint(readable_tracks[0])
        print("\n")
        pp.pprint(readable_tracks[1])
        sleep(1)


if __name__ == '__main__':
    main()

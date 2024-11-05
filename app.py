import logging
import os
import sys

from flask import Flask, session, request, redirect, render_template, jsonify
from flask_session import Session
import spotipy
from werkzeug.exceptions import abort

import app_env  # not stored in git
from recommendation_engine import playlist
from recommendation_engine.mood_track_finder import MoodTrackFinder
from search.autocomplete import search_tracks

# Top level entry point for wave-guide flask application

# App setup =================================
# ===========================================

SONG_MODE = "song"
MOOD_MODE = "mood"


def create_app():
    app = Flask(__name__)
    # note lowercase means flask.session, not flask_session.Session. Should we pick one?
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        cache_handler=cache_handler,
        client_id=app_env.SPOTIPY_CLIENT_ID,
        client_secret=app_env.SPOTIPY_CLIENT_SECRET,
        redirect_uri=app_env.SPOTIPY_REDIRECT_URI,
        scope="user-library-read user-top-read playlist-modify-private",
        open_browser=False,
    )
    spotify = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=45, retries=0)
    app.cache_handler = cache_handler
    app.auth_manager = auth_manager
    app.spotify = spotify
    app.config["SECRET_KEY"] = os.urandom(64)
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = "./.flask_session/"

    # setup logging
    app.logger.setLevel(logging.DEBUG)
    app.logger.info("created app")
    return app


app = create_app()


# App logic =================================
# ===========================================


def validate_token():
    if not app.auth_manager.validate_token(app.cache_handler.get_cached_token()):
        return False
    return True


@app.route("/")
def index():
    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        app.auth_manager.get_access_token(request.args.get("code"))
        return redirect("/")

    if not validate_token():
        # Step 1. Display sign in link when no token
        auth_url = app.auth_manager.get_authorize_url()
        return render_template("login.html", auth_url=auth_url)

    # Step 3. Signed in, display data
    app.spotify = spotipy.Spotify(auth_manager=app.auth_manager)
    user_name = app.spotify.me()["display_name"]
    app.logger.info(f"user {user_name} logged in")
    return render_template("index.html", user_name=user_name)


@app.route("/log_out")
def log_out():
    session.pop("token_info", None)
    return redirect("/")


# TODO: rename to /search or maybe /track_search, /tracks/search
@app.route("/autocomplete", methods=["POST"])
def autocomplete():
    if not request.json or "query" not in request.json:
        abort(400)
    query = request.json["query"]
    if not validate_token():
        return redirect("/")

    limit = 4
    suggestions = search_tracks(app.spotify, query, limit)
    if not suggestions:
        return jsonify({"message": "No suggestions found"}), 404
    return jsonify(suggestions)


@app.route("/new_playlist/", methods=["POST"])
def new_playlist():
    if not validate_token():
        return redirect("/")
    _validate_new_playlist_request(request)

    # track to start the playlist
    source_mode = request.json["source_mode"]
    source_track_id = ""
    if source_mode == SONG_MODE:
        source_track_id = request.json["seed_track_id"]
    elif source_mode == MOOD_MODE:
        track_finder = MoodTrackFinder(app.spotify, request.json["source_mood"], 1)
        source_track_id = track_finder.find()[0]["id"]
    else:
        app.logger.error(f"Unkonwn source mode: {source_mode}. Must provide one of the modes 'song' or 'mood'")
        abort(400)

    # track to end the playlist
    destination_mode = request.json["destination_mode"]
    destination_track_id = ""
    if destination_mode == SONG_MODE:
        destination_track_id = request.json["destination_track_id"]
    elif destination_mode == MOOD_MODE:
        track_finder = MoodTrackFinder(app.spotify, request.json["destination_mood"], 2)
        recs = track_finder.find()
        for rec in recs:
            if rec["id"] != source_track_id:
                destination_track_id = rec["id"]
                break
    else:
        app.logger.error(f"Unkonwn destination mode: {destination_mode}. Must provide one of the modes 'song' or 'mood'")
        abort(400)

    app.logger.info("creating song to song playlist")
    resp = playlist.create_song_to_song_playlist(app.spotify, source_track_id, destination_track_id)
    return jsonify(resp)


def _validate_new_playlist_request(request):
    if not request.json or "source_mode" not in request.json:
        app.logger.error("request must include source_mode")
        abort(400)
    if "destination_mode" not in request.json:
        app.logger.error("request must include destination_mode")
        abort(400)

    source_mode = request.json["source_mode"]
    destination_mode = request.json["destination_mode"]

    if source_mode == SONG_MODE and "seed_track_id" not in request.json:
        app.logger.error("source mode is song but no seed_track_id requeted")
        abort(400)
    if source_mode == MOOD_MODE and "source_mood" not in request.json:
        app.logger.error("source mode is song but no source_mood requeted")
        abort(400)
    if destination_mode == SONG_MODE and "seed_track_id" not in request.json:
        app.logger.error("destination mode is song but no seed_track_id requeted")
        abort(400)
    if destination_mode == MOOD_MODE and "destination_mood" not in request.json:
        app.logger.error("destination mode is song but no destination_mood requeted")
        abort(400)


# Test utility to experiment with feature paramaters
# TODO: make it easier to pass token in
@app.route("/tracks", methods=["GET"])
def get_tracks():
    if not validate_token():
        return redirect("/")
    mood = request.args.get('mood')
    if not mood:
        abort(400, "Include a mood query paramater. Example: /tracks?mood=calm")
    track_finder = MoodTrackFinder(app.spotify, mood, 3)
    recs = track_finder.find()
    wg_resp = {}
    track_ids = []
    for track in recs:
        simplified_track = {
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "url": track["external_urls"]["spotify"]
        }
        wg_resp[track["id"]] = simplified_track
        track_ids.append(track["id"])
    print("getting track features")
    track_features = app.spotify.audio_features(track_ids)
    print("got features")
    for features in track_features:
        wg_resp[features["id"]]["features"] = {
            "acousticness": features["acousticness"],
            "danceability": features["danceability"],
            "energy": features["energy"],
            "instrumentalness": features["instrumentalness"],
            "valence": features["valence"],
            "key": features["key"],
            "liveness": features["liveness"],
            "loudness": features["loudness"],
            "mode": features["mode"],
            "speechiness": features["speechiness"],
            "tempo": features["tempo"],
        }

    return jsonify(wg_resp)

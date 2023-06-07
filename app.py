import os
from flask import Flask, session, request, redirect, render_template, jsonify
from flask_session import Session
from werkzeug.exceptions import abort
import spotipy

import app_env  # not stored in git
from search.autocomplete import search_tracks
from recommendation_engine import controller as recommendation

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
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    app.cache_handler = cache_handler
    app.auth_manager = auth_manager
    app.spotify = spotify
    app.config["SECRET_KEY"] = os.urandom(64)
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = "./.flask_session/"
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
    return render_template("index.html", user_name=app.spotify.me()["display_name"])


@app.route("/log_out")
def log_out():
    session.pop("token_info", None)
    return redirect("/")


@app.route("/autocomplete", methods=["POST"])
def autocomplete():
    if not request.json or not "query" in request.json:
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

    # TODO: move this to reccomendation_engine.controller?
    source_mode = request.json["source_mode"]
    destination_mode = request.json["destination_mode"]

    if source_mode == SONG_MODE and destination_mode == MOOD_MODE:
        seed_track_id = request.json["seed_track_id"]
        mood = request.json["destination_mood"]
        resp = recommendation.create_song_to_mood_playlist(app.spotify, seed_track_id, mood)
        return jsonify(resp)
    elif source_mode == SONG_MODE and destination_mode == SONG_MODE:
        seed_track_id = request.json["seed_track_id"]
        destination_track_id = request.json["destination_track_id"]
        resp = recommendation.create_song_to_song_playlist(app.spotify, seed_track_id, destination_track_id)
        return jsonify(resp)
    elif source_mode == MOOD_MODE and destination_mode == MOOD_MODE:
        source_mood = request.json["source_mood"]
        destination_mood = request.json["destination_mood"]
        resp = recommendation.create_mood_to_mood_playlist(app.spotify, source_mood, destination_mood)
        return jsonify(resp)
    elif source_mode == MOOD_MODE and destination_mode == SONG_MODE:
        source_mood = request.json["source_mood"]
        destination_track_id = request.json["destination_track_id"]
        resp = recommendation.create_mood_to_song_playlist(app.spotify, source_mood, destination_track_id)
        return jsonify(resp)
    # TODO: proper logging
    print(
        f"Unkonwn source mode: {source_mode} or destination mode: {destination_mode} provided.  Must provide one of the modes 'song' or 'mood'"
    )
    abort(400)


def _validate_new_playlist_request(request):
    if not request.json or "source_mode" not in request.json:
        print("request must include source_mode")
        abort(400)
    if "destination_mode" not in request.json:
        print("request must include destination_mode")
        abort(400)

    source_mode = request.json["source_mode"]
    destination_mode = request.json["destination_mode"]

    if source_mode == SONG_MODE and "seed_track_id" not in request.json:
        print("source mode is song but no seed_track_id requeted")
        abort(400)
    if source_mode == MOOD_MODE and "source_mood" not in request.json:
        print("source mode is song but no source_mood requeted")
        abort(400)
    if destination_mode == SONG_MODE and "seed_track_id" not in request.json:
        print("destination mode is song but no seed_track_id requeted")
        abort(400)
    if destination_mode == MOOD_MODE and "destination_mood" not in request.json:
        print("destination mode is song but no destination_mood requeted")
        abort(400)


"""
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
"""

if __name__ == "__main__":
    Session(app)
    app.run(
        threaded=True,
        port=int(os.environ.get("PORT", os.environ.get("SPOTIPY_REDIRECT_URI", 8080).split(":")[-1].split("/")[0])),
    )

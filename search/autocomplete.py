import spotipy


def search_tracks(sp: spotipy.Spotify, query: str, limit: int):  # TODO: add return type
    # if you want to be more specific can use syntax below
    # for now let spotify's api figure out whatever a user would put in
    # query = f"track:{title}, artist:{artist}"
    results = sp.search(query, type="track", offset=0, limit=limit)
    slimmed_results = []
    for result in results["tracks"]["items"]:
        artists = ", ".join(artist["name"] for artist in result["artists"])
        large_image = result["album"]["images"][0]["url"]
        if len(result["album"]["images"]) > 1:
            large_image = result["album"]["images"][1]["url"]
        slimmed = {
            "id": result["id"],
            "artist_name": artists,
            "track_name": result["name"],
            "large_image": large_image,
            "small_image": result["album"]["images"][-1]["url"],
        }
        slimmed_results.append(slimmed)
    return slimmed_results

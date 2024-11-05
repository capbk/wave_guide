import pytest
from unittest.mock import Mock
from recommendation_engine.bookend_seeds_track_finder import BookendSeedsTrackFinder

@pytest.fixture
def mock_spotify():
    mock_sp = Mock()
    # Mock audio_features response
    mock_sp.audio_features.return_value = [
        {
            "energy": 0.8,
            "danceability": 0.7,
            "valence": 0.6,
        },
        {
            "energy": 0.2,
            "danceability": 0.3,
            "valence": 0.4,
        }
    ]
    # Mock recommendations response
    mock_sp.recommendations.return_value = {
        "tracks": [
            {
                "id": "track1",
                "name": "Track 1",
                "artists": [{"id": "artist1", "name": "Artist 1"}]
            },
            {
                "id": "track2",
                "name": "Track 2",
                "artists": [{"id": "artist2", "name": "Artist 2"}]
            }
        ]
    }
    return mock_sp

@pytest.fixture
def seed_track():
    return {
        "id": "seed_id",
        "name": "Seed Track",
        "artists": [{"id": "seed_artist", "name": "Seed Artist"}]
    }

@pytest.fixture
def destination_track():
    return {
        "id": "dest_id",
        "name": "Destination Track",
        "artists": [{"id": "dest_artist", "name": "Destination Artist"}]
    }

def test_init(mock_spotify, seed_track, destination_track):
    finder = BookendSeedsTrackFinder(
        mock_spotify,
        seed_track,
        destination_track
    )
    
    assert finder.num_tracks == 5
    assert finder.source_features == {
        "energy": 0.8,
        "danceability": 0.7,
        "valence": 0.6
    }
    assert finder.destination_features == {
        "energy": 0.2,
        "danceability": 0.3,
        "valence": 0.4
    }

def test_init_with_multipliers(mock_spotify, seed_track, destination_track):
    target_min_multiplier = {"energy": 0.8, "danceability": 0.9}
    target_max_multiplier = {"energy": 1.2, "danceability": 1.1}
    
    finder = BookendSeedsTrackFinder(
        mock_spotify,
        seed_track,
        destination_track,
        target_min_multiplier=target_min_multiplier,
        target_max_multipler=target_max_multiplier
    )
    
    assert finder.target_min_multiplier == target_min_multiplier
    assert finder.target_max_multipler == target_max_multiplier

def test_recommend(mock_spotify, seed_track, destination_track):
    finder = BookendSeedsTrackFinder(
        mock_spotify,
        seed_track,
        destination_track
    )
    
    playlist = finder.recommend()
    
    # Check playlist structure
    assert len(playlist) == 7  # [seed, r0, r1, r2, r3, r4, destination]
    assert playlist[0] == seed_track
    assert playlist[-1] == destination_track
    assert all(track is not None for track in playlist)

    # Verify Spotify API calls
    assert mock_spotify.recommendations.call_count == 5  # One call for each recommendation

def test_skip_duplicate_titles_and_artists():
    recs = {
        "tracks": [
            {
                "name": "Duplicate Track",
                "artists": [{"id": "duplicate_artist"}]
            },
            {
                "name": "Unique Track",
                "artists": [{"id": "unique_artist"}]
            }
        ]
    }
    track_names = ["duplicate track"]
    artist_ids = ["duplicate_artist"]
    
    result = BookendSeedsTrackFinder.skip_duplicate_titles_and_artists(
        recs,
        track_names,
        artist_ids
    )
    
    assert result == {     
        "name": "Unique Track",
        "artists": [{"id": "unique_artist"}]    
    }

def test_skip_duplicate_titles_and_artists_only_dupes_available():
    recs = {
        "tracks": [
            {
                "name": "Duplicate Track",
                "artists": [{"id": "duplicate_artist"}]
            },
            {
                "name": "duplicate track 2",
                "artists": [{"id": "unique_artist"}]
            }
        ]
    }
    track_names = ["duplicate track", "duplicate track 2"]
    artist_ids = ["duplicate_artist"]
    
    result = BookendSeedsTrackFinder.skip_duplicate_titles_and_artists(
        recs,
        track_names,
        artist_ids
    )
    
    assert result == {
        "name": "Duplicate Track",
        "artists": [{"id": "duplicate_artist"}]
    }
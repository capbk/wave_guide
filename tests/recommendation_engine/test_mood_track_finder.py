import pytest
from unittest.mock import Mock, patch
from recommendation_engine.mood_track_finder import (
    MoodTrackFinder,
    MOOD_HAPPY,
    MOOD_ENERGIZED,
    MOOD_CALM,
)


@pytest.fixture
def mock_spotify():
    mock_sp = Mock()
    # Mock the top artists response
    mock_sp.current_user_top_artists.return_value = {
        "total": 5,
        "items": [
            {"id": f"artist_{i}", "name": f"Artist {i}"} for i in range(5)
        ]
    }
    # Mock the recommendations response
    mock_sp.recommendations.return_value = {
        "tracks": [{"id": f"track_{i}"} for i in range(3)]
    }
    return mock_sp


def test_init_valid_mood(mock_spotify):
    finder = MoodTrackFinder(mock_spotify, MOOD_HAPPY, 3)
    assert finder.mood == MOOD_HAPPY
    assert finder.num_tracks == 3


def test_init_invalid_mood(mock_spotify):
    with pytest.raises(ValueError, match="Unknown mood"):
        MoodTrackFinder(mock_spotify, "invalid_mood", 3)


def test_init_invalid_num_tracks(mock_spotify):
    with pytest.raises(ValueError, match="requires num_tracks greater than 0"):
        MoodTrackFinder(mock_spotify, MOOD_HAPPY, 0)


def test_get_top_artists(mock_spotify):
    # top artists are fetched in init
    finder = MoodTrackFinder(mock_spotify, MOOD_HAPPY, 3)
    artists = finder.top_artists
    
    assert len(artists) == 3  # short_term, medium_term, long_term
    assert mock_spotify.current_user_top_artists.call_count == 3


def test_get_seed_artists(mock_spotify):
    finder = MoodTrackFinder(mock_spotify, MOOD_HAPPY, 3)
    seeds = finder.get_seed_artists()
    
    assert len(seeds) <= 5  # Max 5 seeds allowed
    assert all(isinstance(seed, str) for seed in seeds)


def test_find_happy_mood(mock_spotify):
    finder = MoodTrackFinder(mock_spotify, MOOD_HAPPY, 3)
    tracks = finder.find()
    
    assert len(tracks) == 3
    mock_spotify.recommendations.assert_called_once()
    # Verify happy mood features were used
    call_kwargs = mock_spotify.recommendations.call_args[1]
    assert call_kwargs["target_valence"] == 3
    assert call_kwargs["min_valence"] == 0.8


def test_find_energized_mood(mock_spotify):
    finder = MoodTrackFinder(mock_spotify, MOOD_ENERGIZED, 3)
    tracks = finder.find()
    
    call_kwargs = mock_spotify.recommendations.call_args[1]
    assert call_kwargs["target_energy"] == 3
    assert call_kwargs["min_energy"] == 0.71


def test_find_calm_mood(mock_spotify):
    finder = MoodTrackFinder(mock_spotify, MOOD_CALM, 3)
    tracks = finder.find()
    
    call_kwargs = mock_spotify.recommendations.call_args[1]
    assert call_kwargs["target_energy"] == 0.05
    assert call_kwargs["max_energy"] == 0.5


def test_no_top_artists(mock_spotify):
    mock_spotify.current_user_top_artists.return_value = {"total": 0, "items": []}
    finder = MoodTrackFinder(mock_spotify, MOOD_HAPPY, 3)
    artists_per_range = finder._get_top_artists()
    
    assert all(len(artists) == 0 for artists in artists_per_range.values())


def test_empty_session(mock_spotify):
    # Mock the Spotify API response
    mock_spotify.current_user_top_artists.return_value = {
        "total": 2,
        "items": [
            {"name": "Artist 1", "id": "id1"},
            {"name": "Artist 2", "id": "id2"}
        ]
    }

    mock_spotify.recommendations.return_value = {
        "tracks": ["track1", "track2", "track3"]
    }

    mock_session = {}
    finder = MoodTrackFinder(mock_spotify, MOOD_HAPPY, 3, session=mock_session)
    tracks = finder.find()

    # Verify Spotify API was called since session was empty
    assert mock_spotify.current_user_top_artists.call_count == 3  # once for each time range
    assert len(tracks) == 3


def test_none_session(mock_spotify):
    # Mock the Spotify API response
    mock_spotify.current_user_top_artists.return_value = {
        "total": 2,
        "items": [
            {"name": "Artist 1", "id": "id1"},
            {"name": "Artist 2", "id": "id2"}
        ]
    }

    mock_spotify.recommendations.return_value = {
        "tracks": ["track1", "track2", "track3"]
    }

    mock_session = {}
    finder = MoodTrackFinder(mock_spotify, MOOD_HAPPY, 3, session=None)
    tracks = finder.find()
    # Verify Spotify API was called since session was empty
    assert mock_spotify.current_user_top_artists.call_count == 3  # once for each time range
    assert len(tracks) == 3

def test_session_with_stored_artists(mock_spotify):
    mock_session = {
        'top_artists': {
            'short_term': [
                {'id': 'cached_artist_1', 'name': 'Artist One'},
                {'id': 'cached_artist_2', 'name': 'Artist Two'}
            ],
            'medium_term': [
                {'id': 'cached_artist_3', 'name': 'Artist Three'},
                {'id': 'cached_artist_4', 'name': 'Artist Four'}
            ],
            'long_term': [
                {'id': 'cached_artist_5', 'name': 'Artist Five'},
                {'id': 'cached_artist_6', 'name': 'Artist Six'}
            ]
        }
    }

    finder = MoodTrackFinder(mock_spotify, MOOD_HAPPY, 3, session=mock_session)
    tracks = finder.find()

    # Verify Spotify API was NOT called since we used cached artists
    assert mock_spotify.current_user_top_artists.call_count == 0
    assert len(tracks) == 3

    # Verify recommendations were made using cached artists
    call_kwargs = mock_spotify.recommendations.call_args[1]
    assert any('cached_artist' in seed for seed in call_kwargs['seed_artists'])
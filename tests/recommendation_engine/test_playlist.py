import pytest
from unittest.mock import Mock, patch
from recommendation_engine.playlist import create_song_to_song_playlist, _create_playlist

@pytest.fixture
def mock_spotify():
    return Mock()

@pytest.fixture
def mock_track_response():
    return {
        "id": "track123",
        "name": "Test Track",
        "uri": "spotify:track:track123",
    }

@pytest.fixture
def mock_playlist_response():
    return {
        "id": "playlist123",
        "external_urls": {
            "spotify": "https://open.spotify.com/playlist/123"
        },
        "name": "Wave Guide from Test Track A to Test Track B",
        "images": [
            {"url": "https://example.com/playlist-cover.jpg"}
        ]
    }

def test_create_playlist(mock_spotify, mock_track_response):
    # Arrange
    mock_spotify.current_user.return_value = {"id": "test_user"}
    mock_spotify.user_playlist_create.return_value = {"id": "playlist123"}
    mock_spotify.user_playlist.return_value = {
        "external_urls": {"spotify": "https://test-url"},
        "name": "Test Playlist",
        "images": [{"url": "https://test-image"}]
    }
    
    recommendation_uris = ["spotify:track:1", "spotify:track:2"]
    
    # Act
    result = _create_playlist(mock_spotify, recommendation_uris, "Point A", "Point B")
    
    # Assert
    mock_spotify.current_user.assert_called_once()
    mock_spotify.user_playlist_create.assert_called_once_with(
        "test_user", 
        "Wave Guide from Point A to Point B", 
        public=False
    )
    mock_spotify.playlist_add_items.assert_called_once_with("playlist123", recommendation_uris)
    
    assert result["url"] == "https://test-url"
    assert result["name"] == "Test Playlist"
    assert result["image"] == "https://test-image"

@patch('recommendation_engine.playlist.BookendSeedsTrackFinder')
def test_create_song_to_song_playlist(MockBookendFinder, mock_spotify, mock_track_response):
    # Arrange
    seed_track_id = "track123"
    destination_track_id = "track456"
    
    mock_spotify.track.side_effect = [
        {"name": "Track A", "id": seed_track_id},
        {"name": "Track B", "id": destination_track_id}
    ]
    
    mock_finder_instance = Mock()
    mock_finder_instance.recommend.return_value = [
        {"uri": "spotify:track:1"},
        {"uri": "spotify:track:2"}
    ]
    MockBookendFinder.return_value = mock_finder_instance
    
    mock_spotify.user_playlist_create.return_value = {"id": "playlist123"}
    mock_spotify.current_user.return_value = {"id": "test_user"}
    mock_spotify.user_playlist.return_value = {
        "external_urls": {"spotify": "https://test-url"},
        "name": "Test Playlist",
        "images": [{"url": "https://test-image"}]
    }
    
    # Act
    result = create_song_to_song_playlist(mock_spotify, seed_track_id, destination_track_id)
    
    # Assert
    mock_spotify.track.assert_any_call(seed_track_id)
    mock_spotify.track.assert_any_call(destination_track_id)
    
    MockBookendFinder.assert_called_once_with(
        mock_spotify,
        {"name": "Track A", "id": seed_track_id},
        {"name": "Track B", "id": destination_track_id}
    )
    mock_finder_instance.recommend.assert_called_once()
    
    assert result["url"] == "https://test-url"
    assert result["name"] == "Test Playlist"
    assert result["image"] == "https://test-image"

def test_create_playlist_error_handling(mock_spotify):
    # Arrange
    mock_spotify.current_user.side_effect = Exception("API Error")
    
    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        _create_playlist(mock_spotify, ["uri1"], "Point A", "Point B")
    assert str(exc_info.value) == "API Error"

@patch('recommendation_engine.playlist.BookendSeedsTrackFinder')
def test_create_song_to_song_playlist_empty_recommendations(
    MockBookendFinder, 
    mock_spotify, 
    mock_track_response
):
    # Arrange
    mock_finder_instance = Mock()
    mock_finder_instance.recommend.return_value = []
    MockBookendFinder.return_value = mock_finder_instance
    
    mock_spotify.track.return_value = mock_track_response
    mock_spotify.current_user.return_value = {"id": "test_user"}
    mock_spotify.user_playlist_create.return_value = {"id": "playlist123"}
    mock_spotify.user_playlist.return_value = {
        "external_urls": {"spotify": "https://test-url"},
        "name": "Test Playlist",
        "images": [{"url": "https://test-image"}]
    }
    
    # Act
    result = create_song_to_song_playlist(mock_spotify, "track1", "track2")
    
    # Assert
    mock_spotify.playlist_add_items.assert_called_once_with("playlist123", [])
    assert result["url"] == "https://test-url" 
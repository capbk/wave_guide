import pytest
from unittest.mock import Mock, patch
from search.autocomplete import search_tracks

@pytest.fixture
def mock_spotify_response():
    return {
        "tracks": {
            "items": [
                {
                    "id": "track123",
                    "name": "Test Track",
                    "artists": [
                        {"name": "Artist 1"},
                        {"name": "Artist 2"}
                    ],
                    "album": {
                        "images": [
                            {"url": "large_image_1.jpg"},
                            {"url": "large_image_2.jpg"},
                            {"url": "small_image.jpg"}
                        ]
                    }
                }
            ]
        }
    }

@pytest.fixture
def mock_spotify():
    mock_sp = Mock()
    return mock_sp

def test_search_tracks_basic(mock_spotify, mock_spotify_response):
    # Arrange
    mock_spotify.search.return_value = mock_spotify_response
    query = "test query"
    limit = 1

    # Act
    results = search_tracks(mock_spotify, query, limit)

    # Assert
    mock_spotify.search.assert_called_once_with(query, type="track", offset=0, limit=limit)
    
    assert len(results) == 1
    result = results[0]
    assert result["id"] == "track123"
    assert result["artist_name"] == "Artist 1, Artist 2"
    assert result["track_name"] == "Test Track"
    assert result["large_image"] == "large_image_2.jpg"
    assert result["small_image"] == "small_image.jpg"

def test_search_tracks_single_image(mock_spotify):
    # Arrange
    response_single_image = {
        "tracks": {
            "items": [
                {
                    "id": "track123",
                    "name": "Test Track",
                    "artists": [{"name": "Artist 1"}],
                    "album": {
                        "images": [
                            {"url": "only_image.jpg"}
                        ]
                    }
                }
            ]
        }
    }
    mock_spotify.search.return_value = response_single_image
    
    # Act
    results = search_tracks(mock_spotify, "query", 1)

    # Assert
    assert len(results) == 1
    result = results[0]
    assert result["large_image"] == "only_image.jpg"
    assert result["small_image"] == "only_image.jpg"

def test_search_tracks_empty_results(mock_spotify):
    # Arrange
    mock_spotify.search.return_value = {"tracks": {"items": []}}
    
    # Act
    results = search_tracks(mock_spotify, "query", 1)

    # Assert
    assert len(results) == 0

def test_search_tracks_multiple_results(mock_spotify):
    # Arrange
    response_multiple = {
        "tracks": {
            "items": [
                {
                    "id": f"track{i}",
                    "name": f"Track {i}",
                    "artists": [{"name": f"Artist {i}"}],
                    "album": {
                        "images": [
                            {"url": f"large_{i}.jpg"},
                            {"url": f"medium_{i}.jpg"},
                            {"url": f"small_{i}.jpg"}
                        ]
                    }
                } for i in range(3)
            ]
        }
    }
    mock_spotify.search.return_value = response_multiple
    
    # Act
    results = search_tracks(mock_spotify, "query", 3)

    # Assert
    assert len(results) == 3
    for i, result in enumerate(results):
        assert result["id"] == f"track{i}"
        assert result["track_name"] == f"Track {i}"
        assert result["artist_name"] == f"Artist {i}"
        assert result["large_image"] == f"medium_{i}.jpg"
        assert result["small_image"] == f"small_{i}.jpg" 
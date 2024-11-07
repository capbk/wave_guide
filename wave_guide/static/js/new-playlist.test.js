import { createPlaylist, hideModal } from './new-playlist';
import '@testing-library/jest-dom';

// Mock fetch globally
global.fetch = jest.fn();

// Mock DOM elements
document.body.innerHTML = `
  <div id="modal-container">
    <div id="playlist-modal-content"></div>
    <div id="placeholder-playlist-modal-content"></div>
  </div>
`;

describe('Input Validation', () => {
  test('throws error when source song is required but missing', async () => {
    const mockState = {
      getSourceMode: () => 'song',
      getSourceTrackId: () => '',
      getSourceMood: () => '',
      getDestinationMode: () => 'mood',
      getDestinationTrackId: () => '',
      getDestinationMood: () => 'happy'
    };

    await expect(createPlaylist(mockState))
      .rejects
      .toThrow('Please choose a song or mood to start your playlist');
  });

  test('throws error when source mood is required but missing', async () => {
    const mockState = {
      getSourceMode: () => 'mood',
      getSourceTrackId: () => '',
      getSourceMood: () => '',
      getDestinationMode: () => 'mood',
      getDestinationTrackId: () => '',
      getDestinationMood: () => 'happy'
    };

    await expect(createPlaylist(mockState))
      .rejects
      .toThrow('Please choose a song or mood to start your playlist');
  });

  test('throws error when destination song is required but missing', async () => {
    const mockState = {
      getSourceMode: () => 'song',
      getSourceTrackId: () => 'track123',
      getSourceMood: () => '',
      getDestinationMode: () => 'song',
      getDestinationTrackId: () => '',
      getDestinationMood: () => ''
    };

    await expect(createPlaylist(mockState))
      .rejects
      .toThrow('Please choose a song or mood to end your playlist');
  });
});

describe('PlaylistModal', () => {
  beforeEach(() => {
    // Reset fetch mock
    fetch.mockClear();
    // Reset DOM
    document.getElementById('playlist-modal-content').innerHTML = '';
  });

  test('shows loading state correctly', async () => {
    const mockState = {
      getSourceMode: () => 'song',
      getSourceTrackId: () => 'track123',
      getSourceMood: () => '',
      getDestinationMode: () => 'mood',
      getDestinationTrackId: () => '',
      getDestinationMood: () => 'happy'
    };

    // Mock successful API response
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        json: () => Promise.resolve({
          name: 'Test Playlist',
          url: 'https://spotify.com/playlist/123',
          image: 'playlist-image.jpg'
        })
      })
    );

    await createPlaylist(mockState);

    expect(document.getElementById('modal-container').style.display).toBe('block');
  });

  test('renders playlist result correctly', async () => {
    const mockState = {
      getSourceMode: () => 'song',
      getSourceTrackId: () => 'track123',
      getSourceMood: () => '',
      getDestinationMode: () => 'mood',
      getDestinationTrackId: () => '',
      getDestinationMood: () => 'happy'
    };

    const mockResponse = {
      name: 'Test Playlist',
      url: 'https://spotify.com/playlist/123',
      image: 'playlist-image.jpg'
    };

    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        json: () => Promise.resolve(mockResponse)
      })
    );

    await createPlaylist(mockState);

    const modalContent = document.getElementById('playlist-modal-content');
    expect(modalContent.querySelector('.playlist-title')).toHaveTextContent('Test Playlist');
    expect(modalContent.querySelector('.playlist-thumbnail')).toHaveAttribute('src', 'playlist-image.jpg');
    expect(modalContent.querySelector('a.btn')).toHaveAttribute('href', 'https://spotify.com/playlist/123');
  });

  test('hideModal hides the modal', () => {
    hideModal();
    expect(document.getElementById('modal-container').style.display).toBe('none');
    expect(document.getElementById('playlist-modal-content').style.display).toBe('none');
  });
});

describe('API Interaction', () => {
  test('submits playlist request with correct data', async () => {
    const mockState = {
      getSourceMode: () => 'song',
      getSourceTrackId: () => 'track123',
      getSourceMood: () => '',
      getDestinationMode: () => 'mood',
      getDestinationTrackId: () => '',
      getDestinationMood: () => 'happy'
    };

    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        json: () => Promise.resolve({})
      })
    );

    await createPlaylist(mockState);

    expect(fetch).toHaveBeenCalledWith('/new_playlist', {
      method: 'POST',
      body: JSON.stringify({
        source_mode: 'song',
        seed_track_id: 'track123',
        source_mood: '',
        destination_track_id: '',
        destination_mode: 'mood',
        destination_mood: 'happy'
      }),
      headers: {
        'Content-Type': 'application/json'
      }
    });
  });
}); 
import { createPlaylist, hideModal } from './new-playlist';
import '@testing-library/jest-dom';

// Mock fetch globally
global.fetch = jest.fn();

beforeEach(() => {
  // Set up your DOM elements with the complete structure
  document.body.innerHTML = `
    <div id="modal-container">
      <div id="playlist-modal-content">
        <div class="playlist-thumbnail-container"></div>
        <div id="playlist-title"></div>
        <div class="playlist-actions"></div>
      </div>
      <div id="placeholder-playlist-modal-content"></div>
      <div id="playlist-thumbnail"></div>
      <div id="playlist-title"></div>
      <button id="playlist-button"></button>
    </div>
  `;
});

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
  test('shows loading state correctly', async () => {
    const mockState = {
      getSourceMode: () => 'song',
      getSourceTrackId: () => 'track123',
      getSourceMood: () => '',
      getDestinationMode: () => 'mood',
      getDestinationTrackId: () => '',
      getDestinationMood: () => 'happy'
    };

    // Create a promise we can control
    let resolveApiCall;
    const apiPromise = new Promise(resolve => {
      resolveApiCall = resolve;
    });

    // Mock fetch to use our controlled promise
    fetch.mockImplementationOnce(() => apiPromise.then(() => ({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: () => Promise.resolve({
        name: 'Test Playlist',
        url: 'https://spotify.com/playlist/123',
        image: 'playlist-image.jpg'
      })
    })));

    // Start the createPlaylist call but don't await it
    const playlistPromise = createPlaylist(mockState);

    // Check loading state
    expect(document.getElementById('modal-container').style.display).toBe('block');

    // Check for shimmer loading states
    expect(document.getElementById('playlist-title')).toHaveClass('shimmer', 'placeholder-playlist-title');
    expect(document.getElementById('playlist-thumbnail')).toHaveClass('shimmer', 'placeholder-playlist-thumbnail');
    expect(document.getElementById('playlist-button')).toHaveClass('shimmer');
    expect(document.getElementById('playlist-button').textContent).toBe('CREATING PLAYLIST');

    // Resolve the API call
    resolveApiCall();
    // Wait for everything to complete
    await playlistPromise;

    // Check final state
    expect(document.getElementById('modal-container').style.display).toBe('block');
    // Verify shimmer classes are removed (if that's part of your implementation)
    expect(document.getElementById('playlist-title')).not.toHaveClass('shimmer', 'placeholder-playlist-title');
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

    const mockPlaylist = {
      name: 'Test Playlist',
      url: 'https://spotify.com/playlist/123',
      image: 'playlist-image.jpg'
    };

    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: () => Promise.resolve(mockPlaylist)
      })
    );

    await createPlaylist(mockState);

    // Test user-centric behaviors instead of implementation details
    expect(document.body).toHaveTextContent(mockPlaylist.name);

    // Verify the playlist image is visible somewhere on the page
    const playlistImage = document.querySelector('img[src*="playlist-image.jpg"]');
    expect(playlistImage).toBeVisible();

    // Verify users can click through to the playlist
    const playlistLink = document.querySelector(`a[href="${mockPlaylist.url}"]`);
    expect(playlistLink).toBeVisible();
  });

  test('hideModal hides the modal', () => {
    // Set initial display states
    const modalContainer = document.getElementById('modal-container');
    modalContainer.style.display = 'block';
    hideModal();
    expect(modalContainer.style.display).toBe('none');
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
        ok: true,
        status: 200,
        statusText: 'OK',
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
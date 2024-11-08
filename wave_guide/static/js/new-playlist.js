function validateSourceInput(sourceMode, sourceTrackId, sourceMood) {
  if (sourceMode === "song" && !sourceTrackId) {
    throw new Error("Please choose a song or mood to start your playlist");
  }
  if (sourceMode === "mood" && !sourceMood) {
    throw new Error("Please choose a song or mood to start your playlist");
  }
}

function validateDestinationInput(destinationMode, destinationTrackId, destinationMood) {
  if (destinationMode === "song" && !destinationTrackId) {
    throw new Error("Please choose a song or mood to end your playlist");
  }
  if (destinationMode === "mood" && !destinationMood) {
    throw new Error("Please choose a song or mood to end your playlist");
  }
}

// API interaction
async function submitPlaylistRequest(playlistData) {
  const response = await fetch("/new_playlist", {
    method: "POST",
    body: JSON.stringify(playlistData),
    headers: {
      "Content-Type": "application/json",
    },
  });
  return response.json();
}

// UI Components
class PlaylistModal {
  constructor() {
    this.modalContainer = document.getElementById("modal-container");
    this.content = document.getElementById("playlist-modal-content");
    this.thumbnail = document.getElementById("playlist-thumbnail");
    this.title = document.getElementById("playlist-title");
    this.button = document.getElementById("playlist-button");
  }

  showLoading() {
    // Show modal with loading state
    this.modalContainer.style.display = "block";
    this.title.textContent = '';
    const placeholderThumbnail = document.createElement('div');
    placeholderThumbnail.id = 'playlist-thumbnail';
    placeholderThumbnail.classList.add('shimmer', 'placeholder-playlist-thumbnail');
    this.thumbnail.replaceWith(placeholderThumbnail);
    this.thumbnail = placeholderThumbnail;
    
    // Reset title and button to loading state
    this.title.classList.add('shimmer', 'placeholder-playlist-title');
    this.button.classList.add('shimmer');
    this.button.textContent = "CREATING PLAYLIST";
  }

  hideModal() {
    this.modalContainer.style.display = "none";
  }

  renderPlaylistResult(data) {
    // Remove loading states
    this.title.classList.remove("shimmer", "placeholder-playlist-title");
    this.title.classList.add("selected-playlist-title");
    this.button.classList.remove("shimmer");

    // Create new img element
    const thumbnailImg = document.createElement('img');
    thumbnailImg.id = 'playlist-thumbnail';
    thumbnailImg.src = data.image;
    thumbnailImg.alt = 'Playlist Cover';
    thumbnailImg.className = 'selected-thumbnail';

    // Replace the old element
    this.thumbnail.replaceWith(thumbnailImg);
    // Update reference
    this.thumbnail = thumbnailImg;
    
    this.title.textContent = data.name;
    
    // Create new anchor element
    const link = document.createElement('a');
    link.id = 'playlist-button';
    link.href = data.url;
    link.target = '_blank';
    link.className = 'btn';

    // Create Spotify icon
    const icon = document.createElement('img');
    icon.src = 'static/images/spotify_icon.png';
    icon.className = 'spotify-logo';

    // Create text span
    const text = document.createElement('span');
    text.textContent = 'Listen on Spotify';

    // Assemble the elements
    link.appendChild(icon);
    link.appendChild(text);

    // Replace the old button
    this.button.replaceWith(link);
    // Update reference
    this.button = link;
  }
}

// Main function
export async function createPlaylist(state) {
  const modal = new PlaylistModal();
    // Validate inputs
    validateSourceInput(
      state.getSourceMode(),
      state.getSourceTrackId(),
      state.getSourceMood()
    );
    validateDestinationInput(
      state.getDestinationMode(),
      state.getDestinationTrackId(),
      state.getDestinationMood()
    );

    modal.showLoading();

    // Submit request
    const playlistData = {
      source_mode: state.getSourceMode(),
      seed_track_id: state.getSourceTrackId(),
      source_mood: state.getSourceMood(),
      destination_track_id: state.getDestinationTrackId(),
      destination_mode: state.getDestinationMode(),
      destination_mood: state.getDestinationMood(),
    };

    const response = await submitPlaylistRequest(playlistData);
    modal.renderPlaylistResult(response);
}

export const hideModal = () => new PlaylistModal().hideModal();

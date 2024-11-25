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
  if (response.status === 403) {
    alert("Your session has expired. Please log in again.");
    window.location.href = '/';
    return;
  }
  if (!response.ok) {
    throw new Error(`HTTP error. Message: ${response.statusText}. Status: ${response.status}`);
  }
  return response.json();
}

// UI Components
class PlaylistModal {
  constructor() {
    const requiredElements = {
      modalContainer: "modal-container",
      content: "playlist-modal-content",
      thumbnail: "playlist-thumbnail",
      title: "playlist-title",
      button: "playlist-button"
    };

    // Assign all elements and check existence in one go
    Object.entries(requiredElements).forEach(([key, id]) => {
      this[key] = document.getElementById(id);
      if (!this[key]) {
        throw new Error(`Required DOM element "${id}" not found for PlaylistModal`);
      }
    });
  }

  showLoading() {
    this.modalContainer.style.display = "block";
    this.content.style.display = "block";

    this.title.textContent = '';
    this.title.classList.add('shimmer', 'placeholder-playlist-title');

    const placeholderThumbnail = document.createElement('div');
    placeholderThumbnail.id = 'playlist-thumbnail';
    placeholderThumbnail.classList.add('shimmer', 'placeholder-playlist-thumbnail');
    this.thumbnail.replaceWith(placeholderThumbnail);
    this.thumbnail = placeholderThumbnail;
    
    this.button.classList.add('shimmer');
    this.button.textContent = "CREATING PLAYLIST";

  }

  hideModal() {
    this.modalContainer.style.display = "none";
  }

  renderPlaylistResult(data) {
    // Show main content and hide placeholder
    this.content.style.display = "block";
    // Remove loading states
    this.title.classList.remove("shimmer", "placeholder-playlist-title");
    this.title.classList.add("selected-playlist-title");
    this.button.classList.remove("shimmer");

    // Create new img element
    const thumbnailImg = document.createElement('img');
    thumbnailImg.id = 'playlist-thumbnail';
    thumbnailImg.src = data.image;
    thumbnailImg.alt = 'Playlist Cover';
    thumbnailImg.className = 'playlist-thumbnail';

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

  // Show loading state
  modal.showLoading();  // Let the modal class handle all display states

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

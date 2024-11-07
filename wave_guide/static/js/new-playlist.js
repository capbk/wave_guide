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
    this.resultsContent = document.getElementById("playlist-modal-content");
    this.placeholderContent = document.getElementById("placeholder-playlist-modal-content");
  }

  showLoading() {
    this.resultsContent.style.display = "none";
    this.modalContainer.style.display = "block";
    this.placeholderContent.style.display = "block";
  }

  hideModal() {
    this.modalContainer.style.display = "none";
    this.resultsContent.style.display = "none";
    this.resultsContent.innerHTML = "";
  }

  renderPlaylistResult(data) {
    // Create playlist image
    const playlistImage = document.createElement("img");
    playlistImage.classList.add("playlist-thumbnail");
    playlistImage.src = data.image;

    // Create Spotify link with logxo and text
    const playlistLink = document.createElement("a");
    playlistLink.href = data.url;
    playlistLink.classList.add("btn");

    const spotifyLogo = document.createElement("img");
    spotifyLogo.src = "static/images/spotify_icon.png";
    spotifyLogo.classList.add("spotify-logo");
    playlistLink.appendChild(spotifyLogo);

    const linkText = document.createElement("span");
    linkText.innerHTML = "Listen on Spotify";
    playlistLink.appendChild(linkText);

    // Create container structure
    const playlistResultTop = document.createElement("div");
    playlistResultTop.classList.add("playlist-result-top");

    const playlistResultTopRight = document.createElement("div");
    playlistResultTopRight.classList.add("playlist-result-top-right");
    
    // Assemble top section
    playlistResultTop.appendChild(playlistImage);
    playlistResultTopRight.appendChild(playlistLink);
    playlistResultTop.appendChild(playlistResultTopRight);

    // Create and add close button
    const closeSpan = document.createElement("span");
    closeSpan.classList.add("close-modal");
    closeSpan.textContent = "×";
    closeSpan.addEventListener("click", this.hideModal.bind(this));

    // Create playlist title
    const playlistTitle = document.createElement("div");
    playlistTitle.innerHTML = data.name;
    playlistTitle.title = data.name;
    playlistTitle.classList.add("playlist-title");

    // Add everything to results content
    this.resultsContent.appendChild(closeSpan);
    this.resultsContent.appendChild(playlistResultTop);
    this.resultsContent.appendChild(playlistTitle);

    // Update visibility
    this.placeholderContent.style.display = "none";
    this.resultsContent.style.display = "block";
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

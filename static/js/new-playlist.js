// TODO: accept inputs
export function createPlaylist(state) {
  // Validate inputs

  const sourceMode = state.getSourceMode();
  const sourceTrackId = state.getSourceTrackId();
  const sourceMood = state.getSourceMood();
  const destinationTrackId = state.getDestinationTrackId();
  const destinationMood = state.getDestinationMood();
  const destinationMode = state.getDestinationMode();
  if (sourceMode === "song" && !sourceTrackId) {
    alert("Please choose a song or mood to start your playlist");
    // TODO: change cursor focus to search bar
    return;
  }
  if (sourceMode === "mood" && !sourceMood) {
    // TODO: change cursor focus to mood dropdown
    alert("Please choose a song or mood to start your playlist");
    return;
  }
  if (destinationMode === "song" && !destinationTrackId) {
    alert("Please choose a song or mood to end your playlist");
    // TODO: change cursor focus to search bar
    return;
  }
  if (destinationMode === "mood" && !destinationMood) {
    // TODO: change cursor focus to mood dropdown
    alert("Please choose a song or mood to end your playlist");
    return;
  }

  // show loading state
  const modalContainer = document.getElementById("modal-container");
  const resultsContent = document.getElementById("playlist-modal-content");
  const placeholderResultsContent = document.getElementById(
    "placeholder-playlist-modal-content"
  );
  resultsContent.style.display = "none";
  modalContainer.style.display = "block";
  placeholderResultsContent.style.display = "block";

  // Submit form data
  fetch("/new_playlist", {
    method: "POST",
    body: JSON.stringify({
      source_mode: sourceMode,
      seed_track_id: sourceTrackId,
      source_mood: sourceMood,
      destination_track_id: destinationTrackId,
      destination_mode: destinationMode,
      destination_mood: destinationMood,
    }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      const playlistImage = document.createElement("img");
      playlistImage.classList.add("playlist-thumbnail");
      playlistImage.src = data.image;

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

      const playlistResultTop = document.createElement("div");
      playlistResultTop.classList.add("playlist-result-top");

      const playlistResultTopRight = document.createElement("div");
      playlistResultTopRight.classList.add("playlist-result-top-right");
      playlistResultTop.appendChild(playlistImage);
      playlistResultTopRight.appendChild(playlistLink);
      playlistResultTop.appendChild(playlistResultTopRight);

      const closeSpan = document.createElement("span");
      closeSpan.classList.add("close-modal");
      closeSpan.textContent = "×";
      closeSpan.addEventListener("click", hideModal);
      resultsContent.appendChild(closeSpan);
      resultsContent.appendChild(playlistResultTop);

      const playlistTitle = document.createElement("div");
      playlistTitle.innerHTML = data.name;
      playlistTitle.title = data.name;
      playlistTitle.classList.add("playlist-title");
      resultsContent.appendChild(playlistTitle);
      placeholderResultsContent.style.display = "none";
      resultsContent.style.display = "block";
    })
    .catch((error) => {
      console.log(error);
      alert("There was an issue creating your playlist. Sorry.");
    });
}

export function hideModal() {
  const modalContainer = document.getElementById("modal-container");
  modalContainer.style.display = "none";
  const resultsContent = document.getElementById("playlist-modal-content");
  resultsContent.style.display = "none;";
  resultsContent.innerHTML = "";
}

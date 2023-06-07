export function createDebouncedSearch(
  input,
  searchResultsList,
  selectedResultContainer,
  selectedResultPlaceholderContainer,
  location, // source or destination
  state
) {
  let debouncedSearch = _.debounce(function (query) {
    if (query.length === 0) {
      searchResultsList.style.display = "none";
      return;
    }

    fetch("/autocomplete", {
      method: "POST",
      body: JSON.stringify({ query: query }),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        searchResultsList.innerHTML = "";
        for (let i = 0; i < data.length; i++) {
          let item = data[i];
          let li = document.createElement("li");
          li.setAttribute("data-id", item.id);
          li.setAttribute("track_name", item.track_name);
          li.setAttribute("artist_name", item.artist_name);
          li.setAttribute("large_image", item.large_image);
          li.classList.add("search-results-item");
          li.addEventListener("click", function () {
            let selectedId = this.getAttribute("data-id");
            const selectedArtist = this.getAttribute("artist_name");
            const selectedTrackName = this.getAttribute("track_name");
            if (location == "source") {
              state.setSourceTrackId(selectedId);
            } else {
              state.setDestinationTrackId(selectedId);
            }
            searchResultsList.style.display = "none";

            selectedResultContainer.innerHTML = "";
            let trackInfoContainer = document.createElement("div");
            let clickedTitle = document.createElement("div");
            clickedTitle.innerHTML = selectedTrackName;
            clickedTitle.classList.add("selected-title");
            let clickedArtist = document.createElement("div");
            clickedArtist.innerHTML = selectedArtist;
            clickedArtist.classList.add("selected-artist");
            let clickedImg = document.createElement("img");
            clickedImg.src = this.getAttribute("large_image");
            clickedImg.classList.add("selected-thumbnail");
            selectedResultContainer.appendChild(clickedImg);
            trackInfoContainer.appendChild(clickedTitle);
            trackInfoContainer.appendChild(clickedArtist);
            selectedResultContainer.appendChild(trackInfoContainer);
            selectedResultContainer.title = selectedTrackName.concat(
              " by ",
              selectedArtist
            );

            selectedResultPlaceholderContainer.style.display = "none";
            selectedResultContainer.style.display = "block";
          });

          let title = document.createElement("div");
          title.innerHTML = item.track_name;
          title.classList.add("search-result-title");
          let artist = document.createElement("div");
          artist.innerHTML = item.artist_name;
          artist.classList.add("search-result-artist");
          let track_info = document.createElement("div");
          track_info.classList.add("search-result-track-info");
          track_info.appendChild(title);
          track_info.appendChild(artist);
          let img = document.createElement("img");
          img.src = item.small_image;
          img.classList.add("search-result-thumbnail");
          li.title = item.track_name.concat(" by ", item.artist_name);
          li.appendChild(img);
          li.appendChild(track_info);
          searchResultsList.appendChild(li);
        }
        searchResultsList.style.display = "block";
      });
  }, 500);

  input.addEventListener("input", function (e) {
    debouncedSearch(e.target.value);
  });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      let firstResult = searchResultsList.firstChild;
      if (firstResult) {
        firstResult.click();
      }
    }
  });
}

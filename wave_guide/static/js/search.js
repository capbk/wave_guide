function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Helper functions to create DOM elements with attributes and classes
const createElement = (tag, attributes = {}, classes = []) => {
  const element = document.createElement(tag);
  Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
  element.classList.add(...classes);
  return element;
};

// Create the track result HTML structure
const createTrackResultHTML = (item) => {
  const { track_name, artist_name, small_image } = item;
  
  const container = createElement('div', {}, ['search-result-container']);
  
  const img = createElement('img', {
    src: small_image,
    alt: `Album art for ${track_name}`
  }, ['search-result-thumbnail']);
  
  const infoDiv = createElement('div', {}, ['search-result-track-info']);
  const titleDiv = createElement('div', {}, ['search-result-title']);
  titleDiv.textContent = track_name;
  
  const artistDiv = createElement('div', {}, ['search-result-artist']);
  artistDiv.textContent = artist_name;
  
  infoDiv.appendChild(titleDiv);
  infoDiv.appendChild(artistDiv);
  container.appendChild(img);
  container.appendChild(infoDiv);
  
  return container;
};

// Create the selected track HTML structure
const createSelectedTrackHTML = (trackName, artistName, imageUrl) => {
  const container = createElement('div', {}, ['selected-track-container']);
  
  const img = createElement('img', {
    src: imageUrl,
    alt: `Album art for ${trackName}`
  }, ['selected-thumbnail']);
  
  const infoDiv = createElement('div', {}, ['selected-track-info']);
  const titleDiv = createElement('div', {}, ['selected-title']);
  titleDiv.textContent = trackName;
  
  const artistDiv = createElement('div', {}, ['selected-artist']);
  artistDiv.textContent = artistName;
  
  infoDiv.appendChild(titleDiv);
  infoDiv.appendChild(artistDiv);
  container.appendChild(img);
  container.appendChild(infoDiv);
  
  return container;
};

// Handle track selection
const handleTrackSelection = (item, {
  searchResultsList,
  selectedResultContainer,
  selectedResultPlaceholderContainer,
  location,
  state
}) => {
  const { id, track_name, artist_name, large_image } = item;
  
  // Update state
  if (location === "source") {
    state.setSourceTrackId(id);
  } else {
    state.setDestinationTrackId(id);
  }
  
  // Update UI
  searchResultsList.style.display = "none";
  selectedResultContainer.innerHTML = ''; // Clear existing content
  selectedResultContainer.appendChild(
    createSelectedTrackHTML(track_name, artist_name, large_image)
  );
  selectedResultContainer.title = `${track_name} by ${artist_name}`;
  selectedResultPlaceholderContainer.style.display = "none";
  selectedResultContainer.style.display = "block";
};

// Main autocomplete function
export function createDebouncedSearch(
  input,
  searchResultsList,
  selectedResultContainer,
  selectedResultPlaceholderContainer,
  location,
  state
) {
  const searchTracks = async (query) => {
    if (!query) {
      searchResultsList.style.display = "none";
      return;
    }

    try {
      const response = await fetch("/autocomplete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Clear previous results
      searchResultsList.innerHTML = '';
      
      // Create and append results
      data.forEach(item => {
        const li = createElement('li', {
          'data-id': item.id,
          'title': `${item.track_name} by ${item.artist_name}`
        }, ['search-results-item']);
        
        li.innerHTML = createTrackResultHTML(item);
        li.addEventListener('click', () => handleTrackSelection(item, {
          searchResultsList,
          selectedResultContainer,
          selectedResultPlaceholderContainer,
          location,
          state
        }));
        
        searchResultsList.appendChild(li);
      });
      
      searchResultsList.style.display = "block";
    } catch (error) {
      console.error('Error fetching search results:', error);
      searchResultsList.innerHTML = '';
      searchResultsList.style.display = "none";
    }
  };

  const debouncedSearch = debounce(searchTracks, 350);

  // Event listeners
  input.addEventListener("input", (e) => debouncedSearch(e.target.value));
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      searchResultsList.firstChild?.click();
    }
  });
}

export class SearchInput {
    constructor(config) {
        const {
            inputId,
            resultsListId,
            selectedSongId,
            placeholderId,
            location,
            state
        } = config;

        this.input = document.getElementById(inputId);
        this.resultsList = document.getElementById(resultsListId);
        this.selectedSong = document.getElementById(selectedSongId);
        this.placeholder = document.getElementById(placeholderId);
        this.location = location;
        this.state = state;

        this.init();
    }

    init() {
        this.setupSearch();
        this.setupClickOutside();
    }

    setupSearch() {
        createDebouncedSearch(
            this.input,
            this.resultsList,
            this.selectedSong,
            this.placeholder,
            this.location,
            this.state
        );
    }

    setupClickOutside() {
        document.addEventListener("click", (event) => {
            if (!this.resultsList.contains(event.target) && 
                !this.input.contains(event.target)) {
                this.resultsList.style.display = "none";
            }
        });
    }
}

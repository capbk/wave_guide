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

const createTrackResult = (item) => {
  const { track_name, artist_name, small_image } = item;
  
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
  
  return [img, infoDiv];
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

const handleTrackSelection = (item, {
  searchResultsList,
  selectedResultContainer,
  selectedResultPlaceholderContainer,
  location,
  input,
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
  input.classList.remove('search-input-with-results');
  searchResultsList.style.display = "none";
  selectedResultContainer.innerHTML = ''; // Clear existing content
  selectedResultContainer.appendChild(
    createSelectedTrackHTML(track_name, artist_name, large_image)
  );
  selectedResultContainer.title = `${track_name} by ${artist_name}`;
  selectedResultPlaceholderContainer.style.display = "none";
  selectedResultContainer.style.display = "block";
};

// Add this retry utility near the top with other helper functions
const retry = (fn, retriesLeft = 2, interval = 1000) => {
  return new Promise((resolve, reject) => {
    fn()
      .then(resolve)
      .catch((error) => {
        if (retriesLeft === 0) {
          reject(error);
          return;
        }
        setTimeout(() => {
          retry(fn, retriesLeft - 1, interval).then(resolve, reject);
        }, interval);
      });
  });
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
  let currentSelection = -1;

  const updateSelection = (newIndex) => {
    const items = searchResultsList.querySelectorAll('li');
    // Remove hover class from all items first
    items.forEach(item => item.classList.remove('search-results-item-hover'));
    // Update current selection
    currentSelection = newIndex;
    // Add hover class to new selection
    items[currentSelection]?.classList.add('search-results-item-hover');
    // Ensure selected item is visible
    items[currentSelection]?.scrollIntoView({ block: 'nearest' });
  };

  // Add mouse event listeners to each search result item
  const addMouseListeners = () => {
    const items = searchResultsList.querySelectorAll('li');
    items.forEach((item, index) => {
      item.addEventListener('mouseenter', () => {
        updateSelection(index);
      });
    });
  };

  const searchTracks = async (query) => {
    if (!query) {
      searchResultsList.style.display = "none";
      input.classList.remove('search-input-with-results');
      return;
    }

    try {
      const fetchSearch = () =>
        fetch("/autocomplete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query })
        }).then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        });

      const data = await retry(fetchSearch);
      searchResultsList.innerHTML = '';
      input.classList.add('search-input-with-results');

      data.forEach(item => {
        const li = createElement('li', {
          'data-id': item.id,
          'title': `${item.track_name} by ${item.artist_name}`
        }, ['search-results-item']);
        
        const elements = createTrackResult(item);
        elements.forEach(element => li.appendChild(element));

        li.addEventListener('click', () => handleTrackSelection(item, {
          searchResultsList,
          selectedResultContainer,
          selectedResultPlaceholderContainer,
          location,
          input,
          state
        }));

        searchResultsList.appendChild(li);
      });
 
      searchResultsList.style.display = "block";

      // Add this after you populate the search results
      addMouseListeners();
    } catch (error) {
      console.error('Error fetching search results:', error);
      searchResultsList.innerHTML = '';

      const errorLi = createElement('li', {}, ['search-results-item', 'search-error']);
      errorLi.textContent = 'Please refresh the page and try again.';
      searchResultsList.appendChild(errorLi);
      searchResultsList.style.display = "block";
    }
  };

  const debouncedSearch = debounce(searchTracks, 350);

  // Updated event listeners
  input.addEventListener("input", (e) => {
    currentSelection = -1;
    debouncedSearch(e.target.value);
  });

  input.addEventListener("keydown", (e) => {
    const items = searchResultsList.querySelectorAll('li');
    const isVisible = searchResultsList.style.display === "block";

    if (!isVisible || items.length === 0) return;

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        updateSelection(Math.min(currentSelection + 1, items.length - 1));
        break;
      case "ArrowUp":
        e.preventDefault();
        updateSelection(Math.max(currentSelection - 1, 0));
        break;
      case "Enter":
        e.preventDefault();
        if (currentSelection >= 0) {
          items[currentSelection].click();
        } else {
          items[0]?.click();
        }
        break;
      case "Escape":
        searchResultsList.style.display = "none";
        input.classList.remove('search-input-with-results');
        break;
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
                this.input.classList.remove('search-input-with-results');
            }
        });
    }
}

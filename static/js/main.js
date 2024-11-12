import state from "./state.js";
import { SearchInput } from "./search.js";
import { selectMood } from "./mood-select.js";
import { createPlaylist, hideModal } from "./new-playlist.js";

// Constants
const CONSTANTS = {
    LOCATIONS: {
        SOURCE: 'source',
        DESTINATION: 'destination'
    },
    MODES: {
        SONG: 'song'
    }
};

// DOM Setup Functions
function initializeExplainer() {
    const explainerCloseButton = document.getElementById("close-explainer");
    const explainerContainer = document.getElementById("explainer-container");

    explainerCloseButton.addEventListener("click", () => {
        explainerContainer.style.display = "none";
    });

    // Add info button toggle functionality
    document.getElementById('info-btn').addEventListener('click', function() {
        explainerContainer.style.display = explainerContainer.style.display === 'none' ? 'block' : 'none';
    });
}

function initializeSearchInputs() {
    // Source search
    new SearchInput({
        inputId: "source-autocomplete-input",
        resultsListId: "source-search-results-list",
        selectedSongId: "source-selected-song",
        placeholderId: "source-selected-result-placeholder",
        location: CONSTANTS.LOCATIONS.SOURCE,
        state
    });

    // Destination search
    new SearchInput({
        inputId: "destination-autocomplete-input",
        resultsListId: "destination-search-results-list",
        selectedSongId: "destination-selected-song",
        placeholderId: "destination-selected-result-placeholder",
        location: CONSTANTS.LOCATIONS.DESTINATION,
        state
    });
}

function initializePlaylistGeneration() {
    const generatePlaylistButton = document.getElementById("generate-playlist-button");
    generatePlaylistButton.addEventListener("click", async () => {
        clearError(); // Clear any existing error message
        try {
            await createPlaylist(state);
        } catch (error) {
            showError(error.message || "There was an issue creating your playlist. Sorry.");
        }
    });
}

// Error handling
function createErrorContainer() {
    const container = document.createElement("div");
    container.id = "error-message";
    container.className = "error-message";

    // Insert before the generate playlist button
    const generateButton = document.getElementById("generate-playlist-button");
    generateButton.parentNode.insertBefore(container, generateButton);
    return container;
}

function showError(message) {
    const errorContainer = document.getElementById("error-message") || createErrorContainer();
    errorContainer.textContent = message;
    errorContainer.style.display = "block";
}

function clearError() {
    const errorContainer = document.getElementById("error-message");
    if (errorContainer) {
        errorContainer.style.display = "none";
    }
}

// Main Initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeExplainer();
    initializeSearchInputs();
    initializePlaylistGeneration();
    
    // Mode toggles
    setupModeToggle(CONSTANTS.LOCATIONS.SOURCE);
    setupModeToggle(CONSTANTS.LOCATIONS.DESTINATION);
    
    // Mood selections
    setupMoodSelection(CONSTANTS.LOCATIONS.SOURCE);
    setupMoodSelection(CONSTANTS.LOCATIONS.DESTINATION);
    
    // Modal close buttons
    document.querySelectorAll(".close-modal")
        .forEach(button => button.addEventListener("click", hideModal));
});

function setupModeToggle(location) {
    const radioButtons = document.querySelectorAll(`input[name="${location}-mode"]`);
    const songInput = document.getElementById(`${location}-autocomplete-input`);
    const moodSelect = document.getElementById(`${location}-mood-select`);
    const selectedSong = document.getElementById(`${location}-selected-song`);
    const selectedMood = document.getElementById(`${location}-selected-mood`);

    radioButtons.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const mode = e.target.value;
            // Update state
            if (location === CONSTANTS.LOCATIONS.SOURCE) {
                state.setSourceMode(mode);
            } else {
                state.setDestinationMode(mode);
            }
            // Update UI
            if (mode === CONSTANTS.MODES.SONG) {
                songInput.style.display = 'block';
                moodSelect.style.display = 'none';
                selectedSong.style.display = 'block';
                selectedMood.style.display = 'none';
            } else {
                songInput.style.display = 'none';
                moodSelect.style.display = 'block';
                selectedSong.style.display = 'none';
                selectedMood.style.display = 'block';
            }
        });
    });
}

function setupMoodSelection(location) {
    const selectedMoodContainer = document.getElementById(`${location}-selected-mood`);
    const moodSelect = document.getElementById(`${location}-mood-select`);
    
    moodSelect.addEventListener("change", function () {
        const mood = moodSelect.value;
        selectMood(
            mood,
            selectedMoodContainer,
            document.getElementById(`${location}-selected-result-placeholder`)
        );
        // Update state using the appropriate method
        location === CONSTANTS.LOCATIONS.SOURCE ? state.setSourceMood(mood) : state.setDestinationMood(mood);
    });
}

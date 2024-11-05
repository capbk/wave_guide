import state from "./state.js";
import { SearchInput } from "./search.js";
import { selectMood } from "./mood-select.js";
import { createPlaylist, hideModal } from "./new-playlist.js";

const locationSource = "source";
const locationDestination = "destination";
const modeSong = "song";
const modeMood = "mood";

// allow users to close the explainer text
var explainerCloseButton = document.getElementById("close-explainer");
explainerCloseButton.addEventListener("click", function () {
    const explainer = document.getElementById("explainer");
    explainer.style.display = "none";
});

// Replace old tab system with radio button handlers
// ==================================================
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
            if (location === locationSource) {
                state.setSourceMode(mode);
            } else {
                state.setDestinationMode(mode);
            }
            
            // Update UI
            if (mode === modeSong) {
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

// Initialize mode toggles
document.addEventListener('DOMContentLoaded', function() {
    setupModeToggle(locationSource);
    setupModeToggle(locationDestination);
    setupMoodSelection(locationSource);
    setupMoodSelection(locationDestination);
});

// Create source search
new SearchInput({
    inputId: "source-autocomplete-input",
    resultsListId: "source-search-results-list",
    selectedSongId: "source-selected-song",
    placeholderId: "source-selected-result-placeholder",
    location: locationSource,
    state
});

// Create destination search
new SearchInput({
    inputId: "destination-autocomplete-input",
    resultsListId: "destination-search-results-list",
    selectedSongId: "destination-selected-song",
    placeholderId: "destination-selected-result-placeholder",
    location: locationDestination,
    state
});

function closeElementWhenClickElsewhere(event, elementToHide) {
    const clickedElement = event.target;
    if (!elementToHide.contains(clickedElement)) {
        elementToHide.style.display = "none";
    }
}

// Simplified mood selection setup
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
        location === locationSource ? state.setSourceMood(mood) : state.setDestinationMood(mood);
    });
}

// add listeners to generate playlist button
// ==================================================
const generatePlaylistButton = document.getElementById(
    "generate-playlist-button"
);
// TODO: pass inputs to event listener so that we can use variables instead of hidden inputs
generatePlaylistButton.addEventListener("click", function () {
    createPlaylist(state);
});

var modalCloseButtons = document.querySelectorAll(".close-modal");
for (var i = 0; i < modalCloseButtons.length; i++) {
    modalCloseButtons[i].addEventListener("click", hideModal);
}

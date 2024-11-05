import state from "./state.js";
import { createDebouncedSearch } from "./autocomplete.js";
// TODO move ot different file, maybe new-playlist.js?
import { selectMode } from "./mode-tabs.js";
import { selectMood } from "./mood-select.js";
import { createPlaylist, hideModal } from "./new-playlist.js";

const locationSource = "source";
const locationDestination = "destination";
const modeSong = "song";
const modeMood = "mood";

// allow users to close the eplainer text
var explainerCloseButton = document.getElementById("close-explainer");
explainerCloseButton.addEventListener("click", function () {
    const explainer = document.getElementById("explainer");
    explainer.style.display = "none";
});

// add listeners to song/mood tabs
// ==================================================
const sourceMoodTab = document.getElementById("source-mode-tab-mood");
const sourceSongTab = document.getElementById("source-mode-tab-song");
sourceMoodTab.addEventListener("click", function () {
    const mode = modeMood;
    selectMode(locationSource, mode, state);
});
sourceSongTab.addEventListener("click", function () {
    const mode = modeSong;
    selectMode(locationSource, mode, state);
});

const destinationMoodTab = document.getElementById("destination-mode-tab-mood");
const destinationSongTab = document.getElementById("destination-mode-tab-song");
destinationMoodTab.addEventListener("click", function () {
    const mode = modeMood;
    selectMode(locationDestination, mode, state);
});
destinationSongTab.addEventListener("click", function () {
    const mode = modeSong;
    selectMode(locationDestination, mode, state);
});

// TODO: move event listener handling out into this file?
// TODO: return seed and destination track ids rather than using hidden input
// add listeners to autocomplete inputs
// ==================================================
// see `templates/macros/track_input_card.html`
// to see where the inputs to this function come from
const sourceSelectedResultPlaceholder = document.getElementById(
    "source-selected-result-placeholder"
);
const destinationSelectedResultPlaceholder = document.getElementById(
    "destination-selected-result-placeholder"
);

createDebouncedSearch(
    document.getElementById("source-autocomplete-input"),
    document.getElementById("source-search-results-list"),
    document.getElementById("source-selected-song"),
    sourceSelectedResultPlaceholder,
    locationSource,
    state
);
createDebouncedSearch(
    document.getElementById("destination-autocomplete-input"),
    document.getElementById("destination-search-results-list"),
    document.getElementById("destination-selected-song"),
    destinationSelectedResultPlaceholder,
    locationDestination,
    state
);

function closeElementWhenClickElsewhere(event, elementToHide) {
    const clickedElement = event.target;
    if (!elementToHide.contains(clickedElement)) {
        elementToHide.style.display = "none";
    }
}

// close the search results if a user clicks away
document.addEventListener("click", function (event) {
    const elementToHide = document.querySelector(".search-results-list");
    closeElementWhenClickElsewhere(event, elementToHide);
});

// add event listeners for mood selection
// ==================================================
const sourceSelectedMoodContainer = document.getElementById(
    "source-selected-mood"
);
const sourceMoodSelect = document.getElementById("source-mood-select");
sourceMoodSelect.addEventListener("change", function () {
    const mood = sourceMoodSelect.value;
    selectMood(
        mood,
        sourceSelectedMoodContainer,
        sourceSelectedResultPlaceholder
    );
    state.setSourceMood(mood);
});

const destinationSelectedMoodContainer = document.getElementById(
    "destination-selected-mood"
);
const destinationMoodSelect = document.getElementById(
    "destination-mood-select"
);
destinationMoodSelect.addEventListener("change", function () {
    const mood = destinationMoodSelect.value;
    selectMood(
        mood,
        destinationSelectedMoodContainer,
        destinationSelectedResultPlaceholder
    );
    state.setDestinationMood(mood);
});

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

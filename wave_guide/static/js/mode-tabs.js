export function selectMode(location, mode, state) {
  const modeSong = "song";
  const modeMood = "mood";
  const locationSource = "source";
  const locationDestination = "destination";

  if (mode !== modeSong && mode !== modeMood) {
    alert("unknown mode provided: " + mode);
    return;
  }

  if (location !== locationSource && location !== locationDestination) {
    alert("unknown location provided: " + location);
    return;
  }

  let selectedMood = null;
  let selectedTrack = null;

  if (location === locationSource) {
    state.setSourceMode(mode);
    selectedMood = state.getSourceMood();
    selectedTrack = state.getSourceTrackId();
  } else if (location === locationDestination) {
    state.setDestinationMode(mode);
    selectedMood = state.getDestinationMood();
    selectedTrack = state.getDestinationTrackId();
  }

  const selectedTab = document.getElementById(location + "-mode-tab-" + mode);
  if (selectedTab.classList.contains("mode-tab-selected")) {
    return;
  }

  // set defaults for mood mode
  let unselectedTab = document.getElementById(location + "-mode-tab-song");
  let containerToShow = document.getElementById(location + "-mood-select");
  let containerToHide = document.getElementById(
    location + "-autocomplete-input"
  );

  if (mode === modeSong) {
    unselectedTab = document.getElementById(location + "-mode-tab-mood");
    containerToShow = document.getElementById(location + "-autocomplete-input");
    containerToHide = document.getElementById(location + "-mood-select");
  }

  unselectedTab.classList.toggle("mode-tab-selected");
  unselectedTab.classList.toggle("mode-tab");
  selectedTab.classList.toggle("mode-tab");
  selectedTab.classList.toggle("mode-tab-selected");

  containerToHide.style.display = "none";
  containerToShow.style.display = "block";

  // handle thumbnails and track info
  const selectedResultPlaceholder = document.getElementById(
    location + "-selected-result-placeholder"
  );
  const trackInfo = document.getElementById(location + "-selected-song");
  const moodInfo = document.getElementById(location + "-selected-mood");

  if (mode === modeMood) {
    trackInfo.style.display = "none";
    if (selectedMood !== null) {
      selectedResultPlaceholder.style.display = "none";
      moodInfo.style.display = "block";
    } else {
      selectedResultPlaceholder.style.display = "block";
      moodInfo.style.display = "none";
    }
  } else if (mode === modeSong) {
    moodInfo.style.display = "none";
    if (selectedTrack !== null) {
      selectedResultPlaceholder.style.display = "none";
      trackInfo.style.display = "block";
    } else {
      selectedResultPlaceholder.style.display = "block";
      trackInfo.style.display = "none";
    }
  }
}

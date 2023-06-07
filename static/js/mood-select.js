export function selectMood(
    mood,
    selectedResultContainer,
    selectedResultPlaceholder
) {
    const cleanedMood = mood.toLowerCase();
    const moodIcons = {
        happy: "static/images/happy_icon.png",
        energized: "static/images/energized_icon.png",
    };
    if (!(cleanedMood in moodIcons)) {
        notify("unknkown mood " + mood + " selected");
        return;
    }

    selectedResultContainer.innerHTML = "";
    let trackInfoContainer = document.createElement("div");
    let clickedTitle = document.createElement("div");
    clickedTitle.innerHTML = mood + " Mood";
    clickedTitle.classList.add("selected-title");
    let clickedImg = document.createElement("img");
    clickedImg.src = moodIcons[cleanedMood];
    clickedImg.classList.add("selected-thumbnail");
    selectedResultContainer.appendChild(clickedImg);
    trackInfoContainer.appendChild(clickedTitle);
    selectedResultContainer.appendChild(trackInfoContainer);
    selectedResultPlaceholder.style.display = "none";
    selectedResultContainer.style.display = "block";
}

const MOOD_ICONS = {
    happy: 'static/images/happy.png',
    energized: 'static/images/energized.png',
    calm: 'static/images/calm.png',
};

export function selectMood(mood, container, placeholder) {
    const cleanedMood = mood.toLowerCase();
    
    if (!(cleanedMood in MOOD_ICONS)) {
        notify(`Unknown mood "${mood}" selected`);
        return;
    }

    // Clear existing content
    container.textContent = '';

    // Create and append image if icon exists
    const iconPath = MOOD_ICONS[cleanedMood];
    if (iconPath) {
        const img = document.createElement('img');
        img.src = iconPath;
        img.className = 'selected-thumbnail';
        img.alt = `${mood} mood`;
        container.appendChild(img);
    }

    // Create and append title div
    const titleWrapper = document.createElement('div');
    const titleDiv = document.createElement('div');
    titleDiv.className = 'selected-title';
    titleDiv.textContent = `${cleanedMood.charAt(0).toUpperCase() + cleanedMood.slice(1)} Mood`;
    titleWrapper.appendChild(titleDiv);
    container.appendChild(titleWrapper);

    placeholder.style.display = 'none';
    container.style.display = 'block';
}

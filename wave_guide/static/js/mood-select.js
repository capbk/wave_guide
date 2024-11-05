const MOOD_ICONS = {
    happy: 'static/images/happy_icon.png',
    energized: 'static/images/energized_icon.png',
    calm: 'static/images/happy_icon.png', // TODO: add calm icon
};

export function selectMood(mood, container, placeholder) {
    const cleanedMood = mood.toLowerCase();
    
    if (!(cleanedMood in MOOD_ICONS)) {
        notify(`Unknown mood "${mood}" selected`);
        return;
    }

    // Only show image if there's a valid icon path
    const iconPath = MOOD_ICONS[cleanedMood];
    container.innerHTML = `
        ${iconPath ? `<img src="${iconPath}" class="selected-thumbnail" alt="${mood} mood">` : ''}
        <div>
            <div class="selected-title">${mood} Mood</div>
        </div>
    `;

    placeholder.style.display = 'none';
    container.style.display = 'block';
}

import { selectMood } from './mood-select';

describe('Mood Selection', () => {
    let container;
    let placeholder;
    
    beforeEach(() => {
        // Setup DOM elements before each test
        container = document.createElement('div');
        placeholder = document.createElement('div');
        // Mock notify function if it's globally defined
        global.notify = jest.fn();
    });

    afterEach(() => {
        // Clean up after each test
        jest.clearAllMocks();
    });

    test('should display happy mood with icon correctly', () => {
        selectMood('happy', container, placeholder);
        
        expect(container.innerHTML).toContain('static/images/happy.png');
        expect(container.innerHTML).toContain('Happy Mood');
        expect(container.style.display).toBe('block');
        expect(placeholder.style.display).toBe('none');
    });

    test('should display energized mood with icon correctly', () => {
        selectMood('energized', container, placeholder);
        
        expect(container.innerHTML).toContain('static/images/energized.png');
        expect(container.innerHTML).toContain('Energized Mood');
        expect(container.style.display).toBe('block');
        expect(placeholder.style.display).toBe('none');
    });

    test('should handle case-insensitive mood selection', () => {
        selectMood('HAPPY', container, placeholder);
        
        expect(container.innerHTML).toContain('static/images/happy.png');
        expect(container.innerHTML).toContain('Happy Mood');
    });

    test('should notify and return early for unknown mood', () => {
        selectMood('invalid', container, placeholder);
        
        expect(global.notify).toHaveBeenCalledWith('Unknown mood "invalid" selected');
        expect(container.innerHTML).toBe('');
        expect(container.style.display).toBe('');
    });
}); 
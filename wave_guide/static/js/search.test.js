import { createDebouncedSearch, SearchInput } from './search.js';

// Mock fetch globally
global.fetch = jest.fn();

describe('Search functionality', () => {
  let mockState;
  let elements;

  beforeEach(() => {
    // Reset fetch mock
    fetch.mockClear();

    // Setup DOM elements
    elements = {
      input: document.createElement('input'),
      searchResultsList: document.createElement('ul'),
      selectedResultContainer: document.createElement('div'),
      selectedResultPlaceholderContainer: document.createElement('div'),
    };

    // Mock state
    mockState = {
      setSourceTrackId: jest.fn(),
      setDestinationTrackId: jest.fn(),
    };

    // Reset DOM
    document.body.innerHTML = '';
    Object.values(elements).forEach(el => document.body.appendChild(el));
  });

  describe('createDebouncedSearch', () => {
    it('should debounce search requests', async () => {
      jest.useFakeTimers();
      
      const mockResponse = { ok: true, json: () => Promise.resolve([]) };
      fetch.mockResolvedValue(mockResponse);

      createDebouncedSearch(
        elements.input,
        elements.searchResultsList,
        elements.selectedResultContainer,
        elements.selectedResultPlaceholderContainer,
        'source',
        mockState
      );

      // Simulate rapid typing
      elements.input.value = 't';
      elements.input.dispatchEvent(new Event('input'));
      elements.input.value = 'te';
      elements.input.dispatchEvent(new Event('input'));
      elements.input.value = 'tes';
      elements.input.dispatchEvent(new Event('input'));
      elements.input.value = 'test';
      elements.input.dispatchEvent(new Event('input'));

      // Fast-forward debounce timeout
      jest.runAllTimers();

      // Should only make one fetch call with final value
      expect(fetch).toHaveBeenCalledTimes(1);
      expect(fetch).toHaveBeenCalledWith('/autocomplete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: 'test' })
      });

      jest.useRealTimers();
    });

    it('should handle search results correctly', async () => {
      const mockSearchResults = [{
        id: '1',
        track_name: 'Test Track',
        artist_name: 'Test Artist',
        small_image: 'test-image-url'
      }];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockSearchResults)
      });

      createDebouncedSearch(
        elements.input,
        elements.searchResultsList,
        elements.selectedResultContainer,
        elements.selectedResultPlaceholderContainer,
        'source',
        mockState
      );

      // Trigger search
      elements.input.value = 'test';
      elements.input.dispatchEvent(new Event('input'));
      
      // Wait for async operations
      await new Promise(resolve => setTimeout(resolve, 400));

      // Check if results are rendered
      expect(elements.searchResultsList.children.length).toBe(1);
      expect(elements.searchResultsList.innerHTML).toContain('Test Track');
      expect(elements.searchResultsList.innerHTML).toContain('Test Artist');
    });
  });

  describe('SearchInput class', () => {
    it('should initialize correctly', () => {
      // Setup DOM for SearchInput
      document.body.innerHTML = `
        <input id="test-input" />
        <ul id="test-results" />
        <div id="test-selected" />
        <div id="test-placeholder" />
      `;

      const searchInput = new SearchInput({
        inputId: 'test-input',
        resultsListId: 'test-results',
        selectedSongId: 'test-selected',
        placeholderId: 'test-placeholder',
        location: 'source',
        state: mockState
      });

      expect(searchInput.input).toBeTruthy();
      expect(searchInput.resultsList).toBeTruthy();
      expect(searchInput.selectedSong).toBeTruthy();
      expect(searchInput.placeholder).toBeTruthy();
    });

    it('should handle click outside', () => {
      // Setup DOM for SearchInput
      document.body.innerHTML = `
        <input id="test-input" />
        <ul id="test-results" />
        <div id="test-selected" />
        <div id="test-placeholder" />
      `;

      const searchInput = new SearchInput({
        inputId: 'test-input',
        resultsListId: 'test-results',
        selectedSongId: 'test-selected',
        placeholderId: 'test-placeholder',
        location: 'source',
        state: mockState
      });

      // Show results list
      searchInput.resultsList.style.display = 'block';

      // Simulate click outside
      document.body.dispatchEvent(new MouseEvent('click', {
        bubbles: true,
        cancelable: true
      }));

      expect(searchInput.resultsList.style.display).toBe('none');
    });
  });
}); 
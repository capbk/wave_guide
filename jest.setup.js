// Mock lodash debounce
jest.mock('lodash/debounce', () => jest.fn(fn => fn)); 
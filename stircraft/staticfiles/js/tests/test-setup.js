/**
 * Test setup and utilities for StirCraft JavaScript tests
 */

// Mock global objects that our code expects
global.bootstrap = {
    Modal: jest.fn().mockImplementation((element) => ({
        show: jest.fn(),
        hide: jest.fn(),
        getInstance: jest.fn(() => ({
            hide: jest.fn()
        }))
    }))
};

// Mock fetch for API testing
global.fetch = jest.fn();

// Helper to create DOM elements for testing
global.createTestDOM = (html) => {
    document.body.innerHTML = html;
};

// Helper to simulate events
global.simulateEvent = (element, eventType, eventData = {}) => {
    const event = new Event(eventType, { bubbles: true });
    Object.assign(event, eventData);
    element.dispatchEvent(event);
    return event;
};

// Helper to simulate click events with preventDefault
global.simulateClick = (element) => {
    const event = new MouseEvent('click', { bubbles: true });
    event.preventDefault = jest.fn();
    element.dispatchEvent(event);
    return event;
};

// Helper to wait for async operations
global.waitFor = (fn, timeout = 1000) => {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        const check = () => {
            try {
                const result = fn();
                if (result) {
                    resolve(result);
                } else if (Date.now() - startTime > timeout) {
                    reject(new Error('Timeout waiting for condition'));
                } else {
                    setTimeout(check, 10);
                }
            } catch (error) {
                if (Date.now() - startTime > timeout) {
                    reject(error);
                } else {
                    setTimeout(check, 10);
                }
            }
        };
        check();
    });
};

// Reset DOM and mocks before each test
beforeEach(() => {
    document.body.innerHTML = '';
    jest.clearAllMocks();
    
    // Reset window config
    global.window.stirCraftConfig = {
        csrfToken: 'test-csrf-token',
        ingredientAddUrl: '/test/ingredients/add/',
        favoriteUrl: '/test/cocktails/123/favorite/'
    };
    
    // Mock console methods
    global.console.warn = jest.fn();
    global.console.error = jest.fn();
    global.alert = jest.fn();
});

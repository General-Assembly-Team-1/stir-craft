// JavaScript Test Setup for Django Project
// This file runs before JavaScript tests to set up the test environment

// Mock browser environment (only if not already defined)
if (!window.location) {
  Object.defineProperty(window, 'location', {
    value: {
      href: 'http://localhost',
      reload: jest.fn()
    },
    writable: true
  });
}

// Mock Bootstrap if needed
global.bootstrap = {
  Modal: jest.fn().mockImplementation(() => ({
    show: jest.fn(),
    hide: jest.fn()
  }))
};

// Setup document body for tests
document.body.innerHTML = '';

// Mock console methods to reduce noise during testing
global.console = {
  ...console,
  error: jest.fn(),
  warn: jest.fn()
};

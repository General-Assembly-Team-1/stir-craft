// Test setup - runs before each test

// Add TextEncoder/TextDecoder for Node.js compatibility
const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost',
    reload: jest.fn()
  },
  writable: true
});

// Mock Bootstrap if needed
global.bootstrap = {
  Modal: jest.fn().mockImplementation(() => ({
    show: jest.fn(),
    hide: jest.fn()
  }))
};

// Setup document body for tests
document.body.innerHTML = '';

// Mock console methods to reduce noise
global.console = {
  ...console,
  // Uncomment next line to silence console.log during tests
  // log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn()
};

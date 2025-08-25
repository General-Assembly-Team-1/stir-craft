# JavaScript Testing Infrastructure

This directory contains unit tests for the StirCraft JavaScript modules.

## Test Framework

We use Jest for JavaScript unit testing with jsdom for DOM simulation.

## Installation

```bash
npm install --save-dev jest jsdom
```

## Running Tests

```bash
# Run all JavaScript tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

## Test Structure

- `cocktail-form.test.js` - Tests for dynamic ingredient form functionality
- `favorites.test.js` - Tests for favorite/unfavorite functionality  
- `modal-utils.test.js` - Tests for modal utilities
- `test-utils.js` - Shared test utilities and setup

## Test Coverage Areas

### CocktailForm
- Ingredient form addition/removal
- Form validation
- Django formset index management
- Error handling

### FavoritesManager  
- AJAX request handling
- Button state updates
- Success/error notifications
- Loading states

### ModalUtils
- Show/hide functionality
- Keyboard handling (ESC key)
- Click-outside-to-close
- Focus management

## DOM Testing

Tests use jsdom to simulate browser environment and test DOM interactions without requiring a real browser.

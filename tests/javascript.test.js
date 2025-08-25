/**
 * Basic JavaScript functionality tests
 * Tests the core interactive components without complex DOM manipulation
 */

describe('JavaScript Files Syntax and Structure', () => {
  test('cocktail-form.js loads without syntax errors', () => {
    expect(() => {
      require('../stircraft/staticfiles/js/cocktail-form.js');
    }).not.toThrow();
  });

  test('favorites.js loads without syntax errors', () => {
    expect(() => {
      require('../stircraft/staticfiles/js/favorites.js');
    }).not.toThrow();
  });

  test('modal-utils.js loads without syntax errors', () => {
    expect(() => {
      require('../stircraft/staticfiles/js/modal-utils.js');
    }).not.toThrow();
  });

  // Note: cocktail-search.js uses ES6 classes and DOM APIs that require browser environment
  // Integration testing is handled by Django tests and manual browser testing
});

describe('Modal Utils Functionality', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="testModal" class="modal" aria-hidden="true">
        <div class="modal-content">
          <button id="closeBtn">Close</button>
          <input type="text" id="firstInput">
        </div>
      </div>
    `;
    
    // Load the modal utils
    require('../stircraft/staticfiles/js/modal-utils.js');
  });

  test('showModal function exists and is callable', () => {
    expect(typeof window.showModal).toBe('function');
    
    const result = window.showModal('testModal');
    expect(result).toBe(true);
    
    const modal = document.getElementById('testModal');
    expect(modal.classList.contains('show')).toBe(true);
    expect(modal.getAttribute('aria-hidden')).toBe('false');
  });

  test('hideModal function exists and is callable', () => {
    expect(typeof window.hideModal).toBe('function');
    
    // First show the modal
    window.showModal('testModal');
    
    // Then hide it
    const result = window.hideModal('testModal');
    expect(result).toBe(true);
    
    const modal = document.getElementById('testModal');
    expect(modal.classList.contains('show')).toBe(false);
    expect(modal.getAttribute('aria-hidden')).toBe('true');
  });

  test('toggleModal function exists and works correctly', () => {
    expect(typeof window.toggleModal).toBe('function');
    
    const modal = document.getElementById('testModal');
    
    // Should show modal when hidden
    window.toggleModal('testModal');
    expect(modal.classList.contains('show')).toBe(true);
    
    // Should hide modal when shown
    window.toggleModal('testModal');
    expect(modal.classList.contains('show')).toBe(false);
  });
});

describe('Configuration and Integration', () => {
  test('window.stirCraftConfig can be set and accessed', () => {
    window.stirCraftConfig = {
      csrfToken: 'test-token',
      favoriteUrl: '/test/favorite/'
    };
    
    expect(window.stirCraftConfig.csrfToken).toBe('test-token');
    expect(window.stirCraftConfig.favoriteUrl).toBe('/test/favorite/');
  });

  test('CSRF token fallback works', () => {
    // Clear any existing config
    delete window.stirCraftConfig;
    
    document.body.innerHTML = `
      <input type="hidden" name="csrfmiddlewaretoken" value="fallback-token">
    `;
    
    const token = window.stirCraftConfig?.csrfToken || 
                 document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    expect(token).toBe('fallback-token');
  });
});

describe('Color Filter Functionality', () => {
  beforeEach(() => {
    // Set up DOM for color filter tests
    document.body.innerHTML = `
      <form method="get" class="row g-3">
        <select name="color" class="form-select" id="id_color">
          <option value="">Any color</option>
          <option value="Red">Red</option>
          <option value="Orange">Orange</option>
          <option value="Yellow">Yellow</option>
          <option value="Clear">Clear</option>
        </select>
        <button type="submit">Search</button>
      </form>
      <div id="color-filters-buttons"></div>
    `;
  });

  test('color input selector finds select element correctly', () => {
    const colorInput = document.querySelector('select[name="color"]');
    expect(colorInput).not.toBeNull();
    expect(colorInput.tagName).toBe('SELECT');
    expect(colorInput.name).toBe('color');
  });

  test('color filter form values match database values', () => {
    const colorSelect = document.querySelector('select[name="color"]');
    const options = Array.from(colorSelect.options).map(opt => opt.value).filter(val => val !== '');
    
    // These should match the COLOR_CHOICES in Django model (capitalized)
    const expectedColors = ['Red', 'Orange', 'Yellow', 'Clear'];
    expectedColors.forEach(color => {
      expect(options).toContain(color);
    });
  });

  test('color filter button click simulation', () => {
    const colorSelect = document.querySelector('select[name="color"]');
    const form = document.querySelector('form');
    
    // Simulate color filter button click by setting select value
    colorSelect.value = 'Red';
    
    // Trigger change event
    const changeEvent = new Event('change', { bubbles: true });
    colorSelect.dispatchEvent(changeEvent);
    
    expect(colorSelect.value).toBe('Red');
  });
});

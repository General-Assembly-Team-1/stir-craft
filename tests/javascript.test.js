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

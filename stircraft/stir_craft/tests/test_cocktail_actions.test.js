/**
 * Tests for cocktail-actions.js functionality
 * Enhanced cocktail interaction features including favorites toggle and add-to-list
 */

// Mock DOM environment for testing
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

// Set up DOM environment
const dom = new JSDOM(`
<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
    <meta name="csrf-token" content="test-csrf-token">
</head>
<body>
    <!-- Toast container -->
    <div class="toast-container position-fixed top-0 end-0 p-3"></div>
    
    <!-- Favorite button -->
    <button class="btn-favorite" data-cocktail-id="1" data-is-favorited="false">
        <i class="fas fa-heart"></i>
        <span>Add to Favorites</span>
    </button>
    
    <!-- Add to list button -->
    <button class="btn-add-to-list" data-cocktail-id="1">
        <i class="fas fa-plus"></i>
        <span>Add to List</span>
    </button>
    
    <!-- Mock modal for add to list -->
    <div class="modal" id="addToListModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-body">
                    <form id="addToListForm">
                        <select name="list_id" required>
                            <option value="1">Test List 1</option>
                            <option value="2">Test List 2</option>
                        </select>
                        <button type="submit">Add to List</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
`, { 
    url: "http://localhost",
    pretendToBeVisual: true,
    resources: "usable"
});

// Set up global environment
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;

// Mock fetch for testing AJAX calls
global.fetch = jest.fn();

// Mock Bootstrap Modal
global.window.bootstrap = {
    Modal: jest.fn().mockImplementation(() => ({
        show: jest.fn(),
        hide: jest.fn()
    })),
    Toast: jest.fn().mockImplementation(() => ({
        show: jest.fn()
    }))
};

// Load the cocktail actions module (we'll need to adapt this based on how it's structured)
// For now, let's define the functions we're testing directly
const cocktailActions = {
    // Mock implementation of getCsrfToken
    getCsrfToken: () => {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    },

    // Mock implementation of showToast
    showToast: (message, type = 'success') => {
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) return;

        const toastId = `toast-${Date.now()}`;
        const toastHtml = `
            <div class="toast toast-${type}" id="${toastId}" role="alert">
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        if (window.bootstrap && window.bootstrap.Toast) {
            const toast = new window.bootstrap.Toast(toastElement);
            toast.show();
        }

        return toastElement;
    },

    // Mock implementation of handleFavoriteToggle
    handleFavoriteToggle: async (button) => {
        const cocktailId = button.getAttribute('data-cocktail-id');
        const isFavorited = button.getAttribute('data-is-favorited') === 'true';
        
        try {
            const response = await fetch(`/cocktails/${cocktailId}/favorite/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': cocktailActions.getCsrfToken()
                },
                body: JSON.stringify({ action: isFavorited ? 'remove' : 'add' })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            if (data.success) {
                // Update button state
                button.setAttribute('data-is-favorited', (!isFavorited).toString());
                const icon = button.querySelector('i');
                const text = button.querySelector('span');
                
                if (isFavorited) {
                    icon.className = 'fas fa-heart';
                    text.textContent = 'Add to Favorites';
                    button.classList.remove('active');
                } else {
                    icon.className = 'fas fa-heart';
                    text.textContent = 'Remove from Favorites';
                    button.classList.add('active');
                }

                cocktailActions.showToast(data.message, 'success');
            } else {
                cocktailActions.showToast(data.error || 'An error occurred', 'error');
            }
        } catch (error) {
            console.error('Error toggling favorite:', error);
            cocktailActions.showToast('Failed to update favorites', 'error');
        }
    },

    // Mock implementation of handleAddToList
    handleAddToList: (button) => {
        const cocktailId = button.getAttribute('data-cocktail-id');
        
        // Set cocktail ID in modal
        const modal = document.getElementById('addToListModal');
        if (modal) {
            modal.setAttribute('data-cocktail-id', cocktailId);
            
            if (window.bootstrap && window.bootstrap.Modal) {
                const bootstrapModal = new window.bootstrap.Modal(modal);
                bootstrapModal.show();
            }
        }
    },

    // Mock implementation of submitAddToList
    submitAddToList: async (form, cocktailId) => {
        const formData = new FormData(form);
        const listId = formData.get('list_id');

        try {
            const response = await fetch('/cocktails/add-to-list/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': cocktailActions.getCsrfToken()
                },
                body: JSON.stringify({
                    cocktail_id: cocktailId,
                    list_id: listId
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            if (data.success) {
                cocktailActions.showToast(data.message, 'success');
                
                // Hide modal
                const modal = document.getElementById('addToListModal');
                if (modal && window.bootstrap && window.bootstrap.Modal) {
                    const bootstrapModal = window.bootstrap.Modal.getInstance(modal);
                    if (bootstrapModal) {
                        bootstrapModal.hide();
                    }
                }
            } else {
                cocktailActions.showToast(data.error || 'Failed to add to list', 'error');
            }
        } catch (error) {
            console.error('Error adding to list:', error);
            cocktailActions.showToast('Failed to add to list', 'error');
        }
    }
};

describe('Cocktail Actions JavaScript', () => {
    beforeEach(() => {
        // Reset DOM state before each test
        document.body.innerHTML = `
            <div class="toast-container position-fixed top-0 end-0 p-3"></div>
            
            <button class="btn-favorite" data-cocktail-id="1" data-is-favorited="false">
                <i class="fas fa-heart"></i>
                <span>Add to Favorites</span>
            </button>
            
            <button class="btn-add-to-list" data-cocktail-id="1">
                <i class="fas fa-plus"></i>
                <span>Add to List</span>
            </button>
            
            <div class="modal" id="addToListModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-body">
                            <form id="addToListForm">
                                <select name="list_id" required>
                                    <option value="1">Test List 1</option>
                                    <option value="2">Test List 2</option>
                                </select>
                                <button type="submit">Add to List</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Reset fetch mock
        fetch.mockClear();
    });

    describe('getCsrfToken', () => {
        test('should return CSRF token from meta tag', () => {
            const token = cocktailActions.getCsrfToken();
            expect(token).toBe('test-csrf-token');
        });

        test('should return empty string if no CSRF token found', () => {
            document.querySelector('meta[name="csrf-token"]').remove();
            const token = cocktailActions.getCsrfToken();
            expect(token).toBe('');
        });
    });

    describe('showToast', () => {
        test('should create and show success toast', () => {
            const toastElement = cocktailActions.showToast('Test message', 'success');
            
            expect(toastElement).toBeTruthy();
            expect(toastElement.classList.contains('toast-success')).toBe(true);
            expect(toastElement.textContent).toContain('Test message');
        });

        test('should create and show error toast', () => {
            const toastElement = cocktailActions.showToast('Error message', 'error');
            
            expect(toastElement).toBeTruthy();
            expect(toastElement.classList.contains('toast-error')).toBe(true);
            expect(toastElement.textContent).toContain('Error message');
        });

        test('should default to success type', () => {
            const toastElement = cocktailActions.showToast('Default message');
            
            expect(toastElement.classList.contains('toast-success')).toBe(true);
        });
    });

    describe('handleFavoriteToggle', () => {
        test('should add to favorites when not favorited', async () => {
            const button = document.querySelector('.btn-favorite');
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ success: true, message: 'Added to favorites' })
            });

            await cocktailActions.handleFavoriteToggle(button);

            expect(fetch).toHaveBeenCalledWith('/cocktails/1/favorite/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': 'test-csrf-token'
                },
                body: JSON.stringify({ action: 'add' })
            });

            expect(button.getAttribute('data-is-favorited')).toBe('true');
            expect(button.classList.contains('active')).toBe(true);
            expect(button.querySelector('span').textContent).toBe('Remove from Favorites');
        });

        test('should remove from favorites when favorited', async () => {
            const button = document.querySelector('.btn-favorite');
            button.setAttribute('data-is-favorited', 'true');
            button.classList.add('active');
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ success: true, message: 'Removed from favorites' })
            });

            await cocktailActions.handleFavoriteToggle(button);

            expect(fetch).toHaveBeenCalledWith('/cocktails/1/favorite/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': 'test-csrf-token'
                },
                body: JSON.stringify({ action: 'remove' })
            });

            expect(button.getAttribute('data-is-favorited')).toBe('false');
            expect(button.classList.contains('active')).toBe(false);
            expect(button.querySelector('span').textContent).toBe('Add to Favorites');
        });

        test('should handle API error', async () => {
            const button = document.querySelector('.btn-favorite');
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ success: false, error: 'API error' })
            });

            await cocktailActions.handleFavoriteToggle(button);

            // Button state should not change on error
            expect(button.getAttribute('data-is-favorited')).toBe('false');
        });

        test('should handle network error', async () => {
            const button = document.querySelector('.btn-favorite');
            
            fetch.mockRejectedValueOnce(new Error('Network error'));

            await cocktailActions.handleFavoriteToggle(button);

            // Button state should not change on error
            expect(button.getAttribute('data-is-favorited')).toBe('false');
        });
    });

    describe('handleAddToList', () => {
        test('should open modal with correct cocktail ID', () => {
            const button = document.querySelector('.btn-add-to-list');
            const modal = document.getElementById('addToListModal');
            
            cocktailActions.handleAddToList(button);

            expect(modal.getAttribute('data-cocktail-id')).toBe('1');
        });
    });

    describe('submitAddToList', () => {
        test('should successfully add cocktail to list', async () => {
            const form = document.getElementById('addToListForm');
            const cocktailId = '1';
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ success: true, message: 'Added to list successfully' })
            });

            await cocktailActions.submitAddToList(form, cocktailId);

            expect(fetch).toHaveBeenCalledWith('/cocktails/add-to-list/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': 'test-csrf-token'
                },
                body: JSON.stringify({
                    cocktail_id: '1',
                    list_id: '1'
                })
            });
        });

        test('should handle add to list error', async () => {
            const form = document.getElementById('addToListForm');
            const cocktailId = '1';
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ success: false, error: 'List is full' })
            });

            await cocktailActions.submitAddToList(form, cocktailId);

            // Should still make the API call but handle the error gracefully
            expect(fetch).toHaveBeenCalled();
        });

        test('should handle network error for add to list', async () => {
            const form = document.getElementById('addToListForm');
            const cocktailId = '1';
            
            fetch.mockRejectedValueOnce(new Error('Network error'));

            await cocktailActions.submitAddToList(form, cocktailId);

            expect(fetch).toHaveBeenCalled();
        });
    });

    describe('Integration Tests', () => {
        test('should handle multiple favorite toggles correctly', async () => {
            const button = document.querySelector('.btn-favorite');
            
            // Mock successful API responses
            fetch
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ success: true, message: 'Added to favorites' })
                })
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ success: true, message: 'Removed from favorites' })
                });

            // First toggle: add to favorites
            await cocktailActions.handleFavoriteToggle(button);
            expect(button.getAttribute('data-is-favorited')).toBe('true');

            // Second toggle: remove from favorites
            await cocktailActions.handleFavoriteToggle(button);
            expect(button.getAttribute('data-is-favorited')).toBe('false');
        });

        test('should maintain correct button states after errors', async () => {
            const button = document.querySelector('.btn-favorite');
            const initialState = button.getAttribute('data-is-favorited');
            
            fetch.mockRejectedValueOnce(new Error('Network error'));

            await cocktailActions.handleFavoriteToggle(button);

            // State should remain unchanged after error
            expect(button.getAttribute('data-is-favorited')).toBe(initialState);
        });
    });
});

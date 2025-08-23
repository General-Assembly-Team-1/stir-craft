/**
 * Tests for FavoritesManager class
 * Tests favorite/unfavorite functionality and UI updates
 */

describe('FavoritesManager', () => {
    let favoritesHTML;
    
    beforeEach(() => {
        // Create mock favorites DOM structure
        favoritesHTML = `
            <div>
                <input type="hidden" name="csrfmiddlewaretoken" value="test-token">
                
                <button id="favorite-btn" data-cocktail-id="123" class="btn btn-outline-danger">
                    <i id="favorite-icon" class="bi bi-heart"></i>
                    <span id="favorite-text">Add to Favorites</span>
                </button>
            </div>
        `;
        
        createTestDOM(favoritesHTML);
        
        // Load the favorites script
        require('../favorites.js');
    });
    
    describe('Initialization', () => {
        test('should initialize when favorite button exists', () => {
            const favoriteBtn = document.getElementById('favorite-btn');
            expect(favoriteBtn).toBeTruthy();
            expect(favoriteBtn.dataset.cocktailId).toBe('123');
        });
        
        test('should not initialize when no favorite button exists', () => {
            document.body.innerHTML = '<div>No favorite button</div>';
            
            // Should not throw error
            expect(() => {
                require('../favorites.js');
            }).not.toThrow();
        });
    });
    
    describe('Favorite Button Click Handling', () => {
        test('should handle successful favorite request', async () => {
            const favoriteBtn = document.getElementById('favorite-btn');
            const favoriteIcon = document.getElementById('favorite-icon');
            const favoriteText = document.getElementById('favorite-text');
            
            // Mock successful API response
            fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({
                    success: true,
                    favorited: true,
                    message: 'Added to favorites!'
                })
            });
            
            simulateEvent(favoriteBtn, 'click');
            
            // Wait for async operations
            await waitFor(() => fetch.mock.calls.length > 0);
            
            // Check API call
            expect(fetch).toHaveBeenCalledWith(
                '/test/cocktails/1/favorite/',
                expect.objectContaining({
                    method: 'POST',
                    headers: expect.objectContaining({
                        'X-CSRFToken': 'test-csrf-token',
                        'X-Requested-With': 'XMLHttpRequest'
                    })
                })
            );
            
            // Check UI updates for favorited state
            expect(favoriteBtn.className).toBe('btn btn-danger');
            expect(favoriteIcon.className).toBe('bi bi-heart-fill');
            expect(favoriteText.textContent).toBe('Remove from Favorites');
        });
        
        test('should handle successful unfavorite request', async () => {
            const favoriteBtn = document.getElementById('favorite-btn');
            const favoriteIcon = document.getElementById('favorite-icon');
            const favoriteText = document.getElementById('favorite-text');
            
            // Start in favorited state
            favoriteBtn.className = 'btn btn-danger';
            favoriteIcon.className = 'bi bi-heart-fill';
            favoriteText.textContent = 'Remove from Favorites';
            
            // Mock successful unfavorite response
            fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({
                    success: true,
                    favorited: false,
                    message: 'Removed from favorites!'
                })
            });
            
            simulateEvent(favoriteBtn, 'click');
            
            await waitFor(() => fetch.mock.calls.length > 0);
            
            // Check UI updates for unfavorited state
            expect(favoriteBtn.className).toBe('btn btn-outline-danger');
            expect(favoriteIcon.className).toBe('bi bi-heart');
            expect(favoriteText.textContent).toBe('Add to Favorites');
        });
        
        test('should show loading state during request', async () => {
            const favoriteBtn = document.getElementById('favorite-btn');
            const originalContent = favoriteBtn.innerHTML;
            
            // Mock slow API response
            let resolvePromise;
            const slowPromise = new Promise(resolve => {
                resolvePromise = resolve;
            });
            
            fetch.mockReturnValueOnce(slowPromise);
            
            simulateEvent(favoriteBtn, 'click');
            
            // Should be disabled and show loading
            expect(favoriteBtn.disabled).toBe(true);
            expect(favoriteBtn.innerHTML).toContain('Processing...');
            expect(favoriteBtn.innerHTML).toContain('spinner-border');
            
            // Resolve the promise
            resolvePromise({
                json: () => Promise.resolve({
                    success: true,
                    favorited: true,
                    message: 'Added to favorites!'
                })
            });
            
            await waitFor(() => !favoriteBtn.disabled);
            
            // Should restore button state
            expect(favoriteBtn.disabled).toBe(false);
        });
        
        test('should handle API errors gracefully', async () => {
            const favoriteBtn = document.getElementById('favorite-btn');
            
            // Mock API error
            fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({
                    success: false,
                    error: 'Server error'
                })
            });
            
            simulateEvent(favoriteBtn, 'click');
            
            await waitFor(() => fetch.mock.calls.length > 0);
            
            // Should show error notification
            const notification = document.querySelector('.alert-danger');
            expect(notification).toBeTruthy();
            expect(notification.textContent).toContain('Server error');
        });
        
        test('should handle network errors gracefully', async () => {
            const favoriteBtn = document.getElementById('favorite-btn');
            
            // Mock network error
            fetch.mockRejectedValueOnce(new Error('Network error'));
            
            simulateEvent(favoriteBtn, 'click');
            
            await waitFor(() => fetch.mock.calls.length > 0);
            
            // Should show error notification
            const notification = document.querySelector('.alert-danger');
            expect(notification).toBeTruthy();
            expect(notification.textContent).toContain('An error occurred. Please try again.');
        });
        
        test('should handle missing cocktail ID', () => {
            const favoriteBtn = document.getElementById('favorite-btn');
            favoriteBtn.removeAttribute('data-cocktail-id');
            
            // Mock console.error
            global.console.error = jest.fn();
            
            simulateEvent(favoriteBtn, 'click');
            
            expect(global.console.error).toHaveBeenCalledWith(
                'Missing cocktail ID or CSRF token'
            );
            
            // Should show error notification
            const notification = document.querySelector('.alert-danger');
            expect(notification).toBeTruthy();
        });
    });
    
    describe('Notification System', () => {
        test('should show success notifications', async () => {
            const favoriteBtn = document.getElementById('favorite-btn');
            
            fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({
                    success: true,
                    favorited: true,
                    message: 'Test success message'
                })
            });
            
            simulateEvent(favoriteBtn, 'click');
            
            await waitFor(() => document.querySelector('.alert-success'));
            
            const notification = document.querySelector('.alert-success');
            expect(notification).toBeTruthy();
            expect(notification.textContent).toContain('Test success message');
            expect(notification.style.position).toBe('fixed');
            expect(notification.style.top).toBe('20px');
            expect(notification.style.right).toBe('20px');
        });
        
        test('should auto-dismiss notifications after timeout', async () => {
            const favoriteBtn = document.getElementById('favorite-btn');
            
            fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({
                    success: true,
                    favorited: true,
                    message: 'Test message'
                })
            });
            
            simulateEvent(favoriteBtn, 'click');
            
            await waitFor(() => document.querySelector('.alert-success'));
            
            const notification = document.querySelector('.alert-success');
            expect(notification).toBeTruthy();
            
            // Fast-forward timers
            jest.advanceTimersByTime(4000);
            
            // Notification should be removed
            expect(document.querySelector('.alert-success')).toBeFalsy();
        });
    });
    
    describe('Configuration Handling', () => {
        test('should use configuration URLs when available', async () => {
            const favoriteBtn = document.getElementById('favorite-btn');
            
            fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({
                    success: true,
                    favorited: true,
                    message: 'Success'
                })
            });
            
            simulateEvent(favoriteBtn, 'click');
            
            await waitFor(() => fetch.mock.calls.length > 0);
            
            expect(fetch).toHaveBeenCalledWith(
                '/test/cocktails/1/favorite/',
                expect.any(Object)
            );
        });
        
        test('should fallback to DOM CSRF token when config unavailable', async () => {
            // Remove config
            delete window.stirCraftConfig;
            
            const favoriteBtn = document.getElementById('favorite-btn');
            
            fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({
                    success: true,
                    favorited: true,
                    message: 'Success'
                })
            });
            
            simulateEvent(favoriteBtn, 'click');
            
            await waitFor(() => fetch.mock.calls.length > 0);
            
            expect(fetch).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    headers: expect.objectContaining({
                        'X-CSRFToken': 'test-token'
                    })
                })
            );
        });
    });
});

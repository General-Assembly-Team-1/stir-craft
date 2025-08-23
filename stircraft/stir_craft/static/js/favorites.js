/**
 * StirCraft Favorites JavaScript
 * 
 * Handles favorite/unfavorite functionality for cocktails
 * 
 * Features:
 * - AJAX favorite/unfavorite requests
 * - Dynamic button state updates
 * - Success/error notifications
 * - Proper loading states
 * 
 * Dependencies:
 * - Bootstrap 5.x (for alerts and styling)
 * - Django CSRF token handling
 */

class FavoritesManager {
    constructor() {
        this.init();
    }
    
    init() {
        this.bindEvents();
    }
    
    bindEvents() {
        const favoriteBtn = document.getElementById('favorite-btn');
        
        if (favoriteBtn) {
            favoriteBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleFavoriteClick(favoriteBtn);
            });
        }
    }
    
    async handleFavoriteClick(button) {
        const cocktailId = button.dataset.cocktailId;
        const csrfToken = this.getCSRFToken();
        const favoriteUrl = this.getFavoriteUrl(cocktailId);
        
        if (!cocktailId || !csrfToken) {
            console.error('Missing cocktail ID or CSRF token');
            this.showError('Unable to process request. Please refresh the page.');
            return;
        }
        
        // Disable button during request
        this.setButtonLoading(button, true);
        
        try {
            const response = await fetch(favoriteUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateButtonState(button, data.favorited);
                this.showSuccessMessage(data.message);
            } else {
                this.showError(data.error || 'Unknown error');
            }
        } catch (error) {
            console.error('Favorite request error:', error);
            this.showError('An error occurred. Please try again.');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    updateButtonState(button, isFavorited) {
        const favoriteIcon = document.getElementById('favorite-icon');
        const favoriteText = document.getElementById('favorite-text');
        
        if (isFavorited) {
            button.className = 'btn btn-danger';
            if (favoriteIcon) favoriteIcon.className = 'bi bi-heart-fill';
            if (favoriteText) favoriteText.textContent = 'Remove from Favorites';
        } else {
            button.className = 'btn btn-outline-danger';
            if (favoriteIcon) favoriteIcon.className = 'bi bi-heart';
            if (favoriteText) favoriteText.textContent = 'Add to Favorites';
        }
    }
    
    setButtonLoading(button, isLoading) {
        button.disabled = isLoading;
        
        if (isLoading) {
            // Store original content
            button.dataset.originalContent = button.innerHTML;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
        } else {
            // Restore original content
            if (button.dataset.originalContent) {
                button.innerHTML = button.dataset.originalContent;
            }
        }
    }
    
    showSuccessMessage(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'danger');
    }
    
    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 300px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-dismiss after 4 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 4000);
    }
    
    getCSRFToken() {
        // Try configuration first, then DOM
        return window.stirCraftConfig?.csrfToken || 
               document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }
    
    getFavoriteUrl(cocktailId) {
        // Try configuration first, then construct URL
        return window.stirCraftConfig?.favoriteUrl?.replace('0', cocktailId) || 
               `/cocktails/${cocktailId}/favorite/`;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we have a favorite button on the page
    if (document.getElementById('favorite-btn')) {
        new FavoritesManager();
    }
});

// Export for testing (Node.js environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FavoritesManager };
}

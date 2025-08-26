/**
 * StirCraft Favorites JavaScript - New Version
 * 
 * Simple favorites functionality without caching issues
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== NEW FAVORITES JS LOADED ===');
    
    // Handle all favorite buttons (by class, not just single ID)
    const favoriteButtons = document.querySelectorAll('.favorite-btn, #favorite-btn');
    
    if (favoriteButtons.length > 0) {
        console.log(`Found ${favoriteButtons.length} favorite button(s), adding click handlers`);
        
        favoriteButtons.forEach(function(favoriteBtn) {
            favoriteBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                console.log('Favorite button clicked!');
                
                const cocktailId = this.dataset.cocktailId;
                if (!cocktailId) {
                    console.error('No cocktail ID found on button');
                    return;
                }
                
                const csrfToken = getCSRFToken();
                const favoriteUrl = `/cocktails/${cocktailId}/favorite/`;
                
                console.log('Making request to:', favoriteUrl);
                
                // Show immediate feedback
                this.disabled = true;
                const originalText = this.innerHTML;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                
                fetch(favoriteUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Response:', data);
                    
                    if (data.success) {
                        // Update button state
                        if (data.favorited) {
                            this.className = this.className.replace('btn-outline-danger', 'btn-danger');
                            this.innerHTML = '<i class="bi bi-heart-fill"></i> Remove from Favorites';
                            this.setAttribute('data-is-favorited', 'true');
                        } else {
                            this.className = this.className.replace('btn-danger', 'btn-outline-danger');
                            this.innerHTML = '<i class="bi bi-heart"></i> Add to Favorites';
                            this.setAttribute('data-is-favorited', 'false');
                        }
                        
                        // Show success message
                        showNotification(data.message, 'success');
                    } else {
                        this.innerHTML = originalText;
                        showNotification(data.error || 'Unknown error', 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.innerHTML = originalText;
                    showNotification('An error occurred. Please try again.', 'danger');
                })
                .finally(() => {
                    this.disabled = false;
                });
            });
        });
    } else {
        console.log('No favorite buttons found');
    }
});

function getCSRFToken() {
    return window.stirCraftConfig?.csrfToken || 
           document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
}

function showNotification(message, type = 'success') {
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
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-dismiss after 4 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 4000);
}

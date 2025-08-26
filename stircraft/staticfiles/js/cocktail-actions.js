/**
 * Enhanced Cocktail Actions JavaScript
 * Handles favorites, adding to lists, and other cocktail interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeCocktailActions();
});

function initializeCocktailActions() {
    // Initialize favorite button
    const favoriteBtn = document.getElementById('favorite-btn');
    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', handleFavoriteToggle);
    }
    
    // Initialize add to list dropdowns
    const addToListItems = document.querySelectorAll('.add-to-list-item');
    addToListItems.forEach(item => {
        item.addEventListener('click', handleAddToList);
    });
    
    // Initialize toast for notifications
    initializeToast();
}

async function handleFavoriteToggle(event) {
    event.preventDefault();
    
    const btn = event.currentTarget;
    const cocktailId = btn.dataset.cocktailId;
    const isFavorited = btn.dataset.isFavorited === 'true';
    
    // Disable button during request
    btn.disabled = true;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-arrow-clockwise spin"></i> Processing...';
    
    try {
        const response = await fetch(`/cocktails/${cocktailId}/favorite/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': window.stirCraftConfig.csrfToken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update button state
            const icon = btn.querySelector('#favorite-icon');
            const text = btn.querySelector('#favorite-text');
            
            if (data.favorited) {
                btn.className = 'btn btn-danger w-100 action-btn btn-action btn-favorite';
                if (icon) icon.className = 'bi bi-heart-fill fa-heart';
                if (text) text.textContent = 'Remove from Favorites';
                btn.dataset.isFavorited = 'true';
            } else {
                btn.className = 'btn btn-outline-danger w-100 action-btn btn-action btn-favorite';
                if (icon) icon.className = 'bi bi-heart fa-heart';
                if (text) text.textContent = 'Add to Favorites';
                btn.dataset.isFavorited = 'false';
            }
            
            // Show success message
            showToast('Success', data.message, 'success');
        } else {
            btn.innerHTML = originalHTML;
            showToast('Error', data.error || 'Failed to update favorites', 'error');
        }
    } catch (error) {
        console.error('Error toggling favorite:', error);
        btn.innerHTML = originalHTML;
        showToast('Error', 'An unexpected error occurred', 'error');
    } finally {
        btn.disabled = false;
    }
}

async function handleAddToList(event) {
    event.preventDefault();
    
    const item = event.currentTarget;
    const listId = item.dataset.listId;
    const listName = item.dataset.listName;
    const cocktailId = item.dataset.cocktailId;
    
    // Show loading state
    const originalText = item.innerHTML;
    item.innerHTML = '<i class="bi bi-arrow-clockwise spin me-2"></i>Adding...';
    item.disabled = true;
    
    try {
        const response = await fetch(`/cocktails/${cocktailId}/quick-add-to-list/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': window.stirCraftConfig.csrfToken
            },
            body: `list_id=${listId}`
        });
        
        if (response.ok) {
            // Success - show success state
            item.innerHTML = '<i class="bi bi-check-circle text-success me-2"></i>Added!';
            showToast('Success', `Added to "${listName}"`, 'success');
            
            // Update current lists info if it exists
            updateCurrentListsInfo(listName);
            
            // Reset button after delay
            setTimeout(() => {
                item.innerHTML = originalText;
                item.disabled = false;
            }, 2000);
        } else {
            throw new Error('Failed to add to list');
        }
    } catch (error) {
        console.error('Error adding to list:', error);
        showToast('Error', 'Failed to add to list', 'error');
        
        // Reset button
        item.innerHTML = originalText;
        item.disabled = false;
    }
}

function updateCurrentListsInfo(newListName) {
    // Look for existing current lists display and update it
    const currentListsElement = document.querySelector('.text-success small');
    if (currentListsElement && currentListsElement.textContent.includes('This cocktail is in your lists:')) {
        const currentText = currentListsElement.textContent;
        if (!currentText.includes(newListName)) {
            const updatedText = currentText.replace(/:"([^"]+)"/, `: "$1", "${newListName}"`);
            currentListsElement.innerHTML = currentListsElement.innerHTML.replace(currentText, updatedText);
        }
    }
}

function initializeToast() {
    // Make sure Bootstrap toast is available
    if (typeof bootstrap === 'undefined') {
        console.warn('Bootstrap not loaded - toast notifications will not work');
        return;
    }
    
    // Initialize toast element
    const toastElement = document.getElementById('actionToast');
    if (toastElement) {
        window.actionToast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 3000
        });
    }
}

function showToast(title, message, type = 'info') {
    const toastElement = document.getElementById('actionToast');
    const toastTitle = document.getElementById('toast-title');
    const toastBody = document.getElementById('toast-body');
    
    if (!toastElement || !toastTitle || !toastBody) {
        // Fallback to alert if toast not available
        alert(`${title}: ${message}`);
        return;
    }
    
    // Set toast content
    toastTitle.textContent = title;
    toastBody.innerHTML = message;
    
    // Apply styling based on type
    const toastHeader = toastElement.querySelector('.toast-header');
    toastHeader.className = 'toast-header'; // Reset classes
    
    switch (type) {
        case 'success':
            toastHeader.classList.add('bg-success', 'text-white');
            break;
        case 'error':
            toastHeader.classList.add('bg-danger', 'text-white');
            break;
        case 'warning':
            toastHeader.classList.add('bg-warning', 'text-dark');
            break;
        default:
            toastHeader.classList.add('bg-info', 'text-white');
    }
    
    // Show toast
    if (window.actionToast) {
        window.actionToast.show();
    }
}

// CSS animation for spinning loading icon
const spinKeyframes = `
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.spin {
    animation: spin 1s linear infinite;
}
`;

// Add CSS to document
const style = document.createElement('style');
style.textContent = spinKeyframes;
document.head.appendChild(style);

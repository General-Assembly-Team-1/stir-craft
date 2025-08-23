/**
 * StirCraft Search Enhancements JavaScript
 * 
 * Provides enhanced search functionality for the cocktail browser
 * 
 * Features:
 * - Auto-submit search after typing delay
 * - Search suggestions/autocomplete
 * - Quick filter buttons
 * - URL state management
 * - Search history (localStorage)
 * 
 * Dependencies:
 * - None (vanilla JavaScript)
 */

class SearchEnhancements {
    constructor() {
        this.searchForm = document.querySelector('form[method="get"]');
        this.queryInput = document.querySelector('input[name="query"]');
        this.debounceTimeout = null;
        this.debounceDelay = 500; // ms
        
        this.init();
    }
    
    init() {
        if (!this.searchForm) return;
        
        this.bindEvents();
        this.restoreSearchState();
        this.setupQuickFilters();
    }
    
    bindEvents() {
        // Auto-submit after typing delay
        if (this.queryInput) {
            this.queryInput.addEventListener('input', () => {
                this.debounceSearch();
            });
        }
        
        // Handle form submission
        this.searchForm.addEventListener('submit', (e) => {
            this.saveSearchState();
        });
        
        // Handle filter changes
        this.searchForm.querySelectorAll('select').forEach(select => {
            select.addEventListener('change', () => {
                this.debounceSearch();
            });
        });
    }
    
    debounceSearch() {
        clearTimeout(this.debounceTimeout);
        this.debounceTimeout = setTimeout(() => {
            this.submitSearch();
        }, this.debounceDelay);
    }
    
    submitSearch() {
        if (this.isFormValid()) {
            this.saveSearchState();
            this.searchForm.submit();
        }
    }
    
    isFormValid() {
        // Check if at least one field has a value
        const formData = new FormData(this.searchForm);
        for (let [key, value] of formData.entries()) {
            if (value && value.trim() !== '') {
                return true;
            }
        }
        // Allow empty form (show all results)
        return true;
    }
    
    saveSearchState() {
        if (!window.localStorage) return;
        
        const formData = new FormData(this.searchForm);
        const searchState = {};
        
        for (let [key, value] of formData.entries()) {
            searchState[key] = value;
        }
        
        try {
            localStorage.setItem('stircraft_search_state', JSON.stringify(searchState));
        } catch (e) {
            console.warn('Failed to save search state:', e);
        }
    }
    
    restoreSearchState() {
        if (!window.localStorage) return;
        
        try {
            const savedState = localStorage.getItem('stircraft_search_state');
            if (!savedState) return;
            
            const searchState = JSON.parse(savedState);
            
            // Only restore if URL doesn't have parameters (fresh page load)
            if (window.location.search) return;
            
            for (let [key, value] of Object.entries(searchState)) {
                const field = this.searchForm.querySelector(`[name="${key}"]`);
                if (field && value) {
                    field.value = value;
                }
            }
        } catch (e) {
            console.warn('Failed to restore search state:', e);
        }
    }
    
    setupQuickFilters() {
        // Create quick filter buttons for common searches
        const quickFilters = [
            { label: 'Favorites', params: { is_favorited: 'true' } },
            { label: 'Recent', params: { sort_by: '-created_at' } },
            { label: 'Alcoholic', params: { is_alcoholic: 'True' } },
            { label: 'Non-Alcoholic', params: { is_alcoholic: 'False' } }
        ];
        
        const filtersContainer = this.createQuickFiltersContainer();
        if (filtersContainer) {
            quickFilters.forEach(filter => {
                const button = this.createQuickFilterButton(filter);
                filtersContainer.appendChild(button);
            });
        }
    }
    
    createQuickFiltersContainer() {
        const existingContainer = document.getElementById('quick-filters');
        if (existingContainer) return existingContainer;
        
        const container = document.createElement('div');
        container.id = 'quick-filters';
        container.className = 'mb-3';
        container.innerHTML = '<small class="text-muted me-2">Quick filters:</small>';
        
        // Insert before the search form
        this.searchForm.parentNode.insertBefore(container, this.searchForm);
        return container;
    }
    
    createQuickFilterButton(filter) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-sm btn-outline-secondary me-2';
        button.textContent = filter.label;
        
        button.addEventListener('click', () => {
            // Clear form first
            this.clearForm();
            
            // Apply filter parameters
            for (let [key, value] of Object.entries(filter.params)) {
                const field = this.searchForm.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = value;
                }
            }
            
            // Submit the form
            this.submitSearch();
        });
        
        return button;
    }
    
    clearForm() {
        const inputs = this.searchForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
    }
    
    // Public API for other scripts
    setQuery(query) {
        if (this.queryInput) {
            this.queryInput.value = query;
            this.debounceSearch();
        }
    }
    
    addFilter(key, value) {
        const field = this.searchForm.querySelector(`[name="${key}"]`);
        if (field) {
            field.value = value;
            this.debounceSearch();
        }
    }
    
    clearAllFilters() {
        this.clearForm();
        this.submitSearch();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we have a search form on the page
    if (document.querySelector('form[method="get"]')) {
        window.searchEnhancements = new SearchEnhancements();
    }
});

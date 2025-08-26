/**
 * StirCraft Cocktail Search & Filter JavaScript
 * 
 * Enhanced search functionality for the cocktail index page
 * 
 * Features:
 * - Real-time search with debouncing
 * - Tag-based filtering
 * - Color filtering
 * - Alcoholic/Non-alcoholic filtering
 * - Sort options
 * - URL state management
 * - Quick filter buttons
 * - Search history
 * 
 * Dependencies:
 * - None (vanilla JavaScript)
 */

class CocktailSearch {
    constructor() {
        this.searchForm = document.querySelector('form[method="get"]');
        this.queryInput = document.querySelector('input[name="query"]');
        this.ingredientSelect = document.querySelector('select[name="ingredient"]');
        this.spiritSelect = document.querySelector('select[name="spirit"]');
        this.vesselSelect = document.querySelector('select[name="vessel"]');
        this.alcoholicSelect = document.querySelector('select[name="is_alcoholic"]');
        this.colorInput = document.querySelector('select[name="color"]');
        this.sortSelect = document.querySelector('select[name="sort_by"]');
        
        this.debounceTimeout = null;
        this.debounceDelay = 500; // ms
        
        this.init();
    }
    
    init() {
        if (!this.searchForm) return;
        
        this.bindEvents();
        this.createQuickFilters();
        this.createTagFilters();
        this.createColorFilters();
        this.restoreSearchState();
        this.addSearchSuggestions();
    }
    
    bindEvents() {
        // Text search with debouncing
        if (this.queryInput) {
            this.queryInput.addEventListener('input', () => {
                this.debounceSearch();
            });
        }
        
        // Color select with immediate submit
        if (this.colorInput) {
            this.colorInput.addEventListener('change', () => {
                this.submitSearch();
            });
        }
        
        // Immediate submit for dropdowns
        [this.ingredientSelect, this.spiritSelect, this.vesselSelect, this.alcoholicSelect, this.sortSelect].forEach(select => {
            if (select) {
                select.addEventListener('change', () => {
                    this.submitSearch();
                });
            }
        });
        
        // Form submission handler
        this.searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitSearch();
        });
        
        // Clear button
        const clearButton = document.querySelector('a[href*="cocktail_index"]');
        if (clearButton) {
            clearButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.clearAllFilters();
            });
        }
    }
    
    debounceSearch() {
        clearTimeout(this.debounceTimeout);
        this.debounceTimeout = setTimeout(() => {
            this.submitSearch();
        }, this.debounceDelay);
    }
    
    submitSearch() {
        this.saveSearchState();
        this.searchForm.submit();
    }
    
    createQuickFilters() {
        const quickFilters = [
            { 
                label: '🍸 All Cocktails', 
                params: {},
                tooltip: 'Show all cocktails'
            },
            { 
                label: '🥃 Alcoholic', 
                params: { is_alcoholic: 'True' },
                tooltip: 'Show only alcoholic drinks'
            },
            { 
                label: '🚫 Non-Alcoholic', 
                params: { is_alcoholic: 'False' },
                tooltip: 'Show only mocktails and non-alcoholic drinks'
            },
            { 
                label: '🆕 Newest', 
                params: { sort_by: '-created_at' },
                tooltip: 'Sort by newest first'
            },
            { 
                label: '📝 A-Z', 
                params: { sort_by: 'name' },
                tooltip: 'Sort alphabetically'
            }
        ];
        
        const container = this.createQuickFiltersContainer();
        if (container) {
            quickFilters.forEach(filter => {
                const button = this.createQuickFilterButton(filter);
                container.appendChild(button);
            });
        }
        
        // Add spirit-specific filters
        this.createSpiritFilters();
    }
    
    createTagFilters() {
        // Create common tag filters
        const tagFilters = [
            { label: '🌴 Tropical', query: 'tropical' },
            { label: '🎉 Party', query: 'party' },
            { label: '❄️ Frozen', query: 'frozen' },
            { label: '🌙 Night', query: 'night' },
            { label: '☀️ Summer', query: 'summer' },
            { label: '🍎 Fall', query: 'fall autumn' },
            { label: '❄️ Winter', query: 'winter cozy' },
            { label: '🌸 Spring', query: 'spring fresh' },
            { label: '💕 Romantic', query: 'romantic date' },
            { label: '🏠 Cozy', query: 'cozy comfort' }
        ];
        
        const container = this.createTagFiltersContainer();
        if (container) {
            tagFilters.forEach(filter => {
                const button = this.createTagFilterButton(filter);
                container.appendChild(button);
            });
        }
    }
    
    createSpiritFilters() {
        // Create spirit-based filter buttons
        const spiritFilters = [
            { label: '🥃 Rum Cocktails', spirit: 'rum' },
            { label: '🍸 Gin Cocktails', spirit: 'gin' },
            { label: '🥄 Vodka Cocktails', spirit: 'vodka' },
            { label: '🥃 Whiskey Cocktails', spirit: 'whiskey bourbon rye scotch' },
            { label: '🍷 Brandy Cocktails', spirit: 'brandy' }
        ];
        
        const container = this.createSpiritFiltersContainer();
        if (container) {
            spiritFilters.forEach(filter => {
                const button = this.createSpiritFilterButton(filter);
                container.appendChild(button);
            });
        }
    }
    
    createColorFilters() {
        const colorFilters = [
            { label: '🔴 Red', color: 'Red', hex: '#dc3545' },
            { label: '🟠 Orange', color: 'Orange', hex: '#fd7e14' },
            { label: '🟡 Yellow', color: 'Yellow', hex: '#ffc107' },
            { label: '🟢 Green', color: 'Green', hex: '#198754' },
            { label: '🔵 Blue', color: 'Blue', hex: '#0d6efd' },
            { label: '🟣 Purple', color: 'Purple', hex: '#6f42c1' },
            { label: '🟤 Brown', color: 'Brown', hex: '#8B4513' },
            { label: '⚪ Clear', color: 'Clear', hex: '#f8f9fa' },
            { label: '⚫ Black', color: 'Black', hex: '#212529' }
        ];
        
        const container = this.createColorFiltersContainer();
        if (container) {
            colorFilters.forEach(filter => {
                const button = this.createColorFilterButton(filter);
                container.appendChild(button);
            });
        }
    }
    
    createQuickFiltersContainer() {
        const existingContainer = document.getElementById('quick-filters');
        if (existingContainer) return existingContainer;
        
        const container = document.createElement('div');
        container.id = 'quick-filters';
        container.className = 'mb-3';
        container.innerHTML = '<div class="row"><div class="col-12"><small class="text-muted me-2"><strong>Quick Filters:</strong></small></div></div><div class="row"><div class="col-12" id="quick-filters-buttons"></div></div>';
        
        // Insert before the search form
        this.searchForm.parentNode.insertBefore(container, this.searchForm);
        return container.querySelector('#quick-filters-buttons');
    }
    
    createTagFiltersContainer() {
        const existingContainer = document.getElementById('tag-filters');
        if (existingContainer) return existingContainer;
        
        const container = document.createElement('div');
        container.id = 'tag-filters';
        container.className = 'mb-3';
        container.innerHTML = '<div class="row"><div class="col-12"><small class="text-muted me-2"><strong>Filter by Vibe:</strong></small></div></div><div class="row"><div class="col-12" id="tag-filters-buttons"></div></div>';
        
        // Insert after quick filters
        const quickFilters = document.getElementById('quick-filters');
        if (quickFilters) {
            quickFilters.parentNode.insertBefore(container, quickFilters.nextSibling);
        } else {
            this.searchForm.parentNode.insertBefore(container, this.searchForm);
        }
        return container.querySelector('#tag-filters-buttons');
    }
    
    createColorFiltersContainer() {
        const existingContainer = document.getElementById('color-filters');
        if (existingContainer) return existingContainer;
        
        const container = document.createElement('div');
        container.id = 'color-filters';
        container.className = 'mb-3';
        container.innerHTML = '<div class="row"><div class="col-12"><small class="text-muted me-2"><strong>Filter by Color:</strong></small></div></div><div class="row"><div class="col-12" id="color-filters-buttons"></div></div>';
        
        // Insert after tag filters
        const tagFilters = document.getElementById('tag-filters');
        if (tagFilters) {
            tagFilters.parentNode.insertBefore(container, tagFilters.nextSibling);
        } else {
            this.searchForm.parentNode.insertBefore(container, this.searchForm);
        }
        return container.querySelector('#color-filters-buttons');
    }
    
    createSpiritFiltersContainer() {
        const existingContainer = document.getElementById('spirit-filters');
        if (existingContainer) return existingContainer;
        
        const container = document.createElement('div');
        container.id = 'spirit-filters';
        container.className = 'mb-3';
        container.innerHTML = '<div class="row"><div class="col-12"><small class="text-muted me-2"><strong>Filter by Spirit:</strong></small></div></div><div class="row"><div class="col-12" id="spirit-filters-buttons"></div></div>';
        
        // Insert after color filters
        const colorFilters = document.getElementById('color-filters');
        if (colorFilters) {
            colorFilters.parentNode.insertBefore(container, colorFilters.nextSibling);
        } else {
            this.searchForm.parentNode.insertBefore(container, this.searchForm);
        }
        return container.querySelector('#spirit-filters-buttons');
    }
    
    createQuickFilterButton(filter) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-sm btn-outline-primary me-2 mb-2';
        button.textContent = filter.label;
        
        if (filter.tooltip) {
            button.title = filter.tooltip;
        }
        
        button.addEventListener('click', () => {
            this.applyFilter(filter.params);
        });
        
        return button;
    }
    
    createTagFilterButton(filter) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-sm btn-outline-secondary me-2 mb-2';
        button.textContent = filter.label;
        button.title = `Search for ${filter.query} cocktails`;
        
        button.addEventListener('click', () => {
            if (this.queryInput) {
                this.queryInput.value = filter.query;
                this.submitSearch();
            }
        });
        
        return button;
    }
    
    createColorFilterButton(filter) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-sm btn-outline-dark me-2 mb-2';
        button.textContent = filter.label;
        button.title = `Filter by ${filter.color} cocktails`;
        button.style.borderColor = filter.hex;
        
        // Add color indicator
        if (filter.color !== 'Clear') {
            button.style.background = `linear-gradient(45deg, ${filter.hex}22, transparent)`;
        }
        
        button.addEventListener('click', () => {
            if (this.colorInput) {
                this.colorInput.value = filter.color;
                this.submitSearch();
            }
        });
        
        return button;
    }
    
    createSpiritFilterButton(filter) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-sm btn-outline-warning me-2 mb-2';
        button.textContent = filter.label;
        button.title = `Find cocktails made with ${filter.spirit}`;
        
        button.addEventListener('click', () => {
            if (this.queryInput) {
                this.queryInput.value = filter.spirit;
                this.submitSearch();
            }
        });
        
        return button;
    }
    
    applyFilter(params) {
        // Clear form first
        this.clearForm();
        
        // Apply filter parameters
        for (let [key, value] of Object.entries(params)) {
            const field = this.searchForm.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = value;
            }
        }
        
        this.submitSearch();
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
    
    clearAllFilters() {
        this.clearForm();
        this.clearSearchState();
        // Redirect to clean URL
        window.location.href = this.searchForm.action || window.location.pathname;
    }
    
    saveSearchState() {
        if (!window.localStorage) return;
        
        const formData = new FormData(this.searchForm);
        const searchState = {};
        
        for (let [key, value] of formData.entries()) {
            if (value && value.trim() !== '') {
                searchState[key] = value;
            }
        }
        
        try {
            localStorage.setItem('stircraft_cocktail_search_state', JSON.stringify(searchState));
        } catch (e) {
            console.warn('Failed to save search state:', e);
        }
    }
    
    restoreSearchState() {
        if (!window.localStorage) return;
        
        try {
            const savedState = localStorage.getItem('stircraft_cocktail_search_state');
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
    
    clearSearchState() {
        if (window.localStorage) {
            try {
                localStorage.removeItem('stircraft_cocktail_search_state');
            } catch (e) {
                console.warn('Failed to clear search state:', e);
            }
        }
    }
    
    addSearchSuggestions() {
        if (!this.queryInput) return;
        
        // Common search terms for suggestions
        const suggestions = [
            'margarita', 'mojito', 'martini', 'old fashioned', 'manhattan',
            'whiskey', 'gin', 'vodka', 'rum', 'tequila', 'bourbon', 'rye', 'scotch',
            'tropical', 'frozen', 'summer', 'winter', 'party',
            'red', 'blue', 'green', 'clear', 'dark'
        ];
        
        // Create datalist for autocomplete
        const datalist = document.createElement('datalist');
        datalist.id = 'cocktail-search-suggestions';
        
        suggestions.forEach(suggestion => {
            const option = document.createElement('option');
            option.value = suggestion;
            datalist.appendChild(option);
        });
        
        document.body.appendChild(datalist);
        this.queryInput.setAttribute('list', 'cocktail-search-suggestions');
    }
    
    // Public API methods
    search(query) {
        if (this.queryInput) {
            this.queryInput.value = query;
            this.submitSearch();
        }
    }
    
    filterByColor(color) {
        if (this.colorInput) {
            this.colorInput.value = color;
            this.submitSearch();
        }
    }
    
    filterByAlcoholic(isAlcoholic) {
        if (this.alcoholicSelect) {
            this.alcoholicSelect.value = isAlcoholic ? 'True' : 'False';
            this.submitSearch();
        }
    }
    
    setSort(sortBy) {
        if (this.sortSelect) {
            this.sortSelect.value = sortBy;
            this.submitSearch();
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we have a search form on the cocktails page
    if (document.querySelector('form[method="get"]') && window.location.pathname.includes('cocktail')) {
        window.cocktailSearch = new CocktailSearch();
        
        // Add global convenience functions
        window.searchCocktails = function(query) {
            if (window.cocktailSearch) {
                window.cocktailSearch.search(query);
            }
        };
        
        window.filterCocktailsByColor = function(color) {
            if (window.cocktailSearch) {
                window.cocktailSearch.filterByColor(color);
            }
        };
        
        window.filterCocktailsByAlcoholic = function(isAlcoholic) {
            if (window.cocktailSearch) {
                window.cocktailSearch.filterByAlcoholic(isAlcoholic);
            }
        };
    }
});

// Enhanced keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="query"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    
    // Escape to clear search
    if (e.key === 'Escape') {
        const searchInput = document.querySelector('input[name="query"]');
        if (searchInput && document.activeElement === searchInput) {
            if (window.cocktailSearch) {
                window.cocktailSearch.clearAllFilters();
            }
        }
    }
});

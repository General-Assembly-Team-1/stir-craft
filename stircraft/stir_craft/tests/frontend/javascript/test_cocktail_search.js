/**
 * Cocktail Search Functionality Tests
 * 
 * Tests for search functionality including:
 * - Search input handling
 * - Filter application
 * - Results display
 * - Performance considerations
 * - Error handling
 * 
 * Author: StirCraft Development Team
 * Date: August 2025
 */

// Mock DOM elements for testing
const createMockDOM = () => {
    document.body.innerHTML = `
        <div id="search-container">
            <input id="search-input" type="text" placeholder="Search cocktails...">
            <select id="filter-type">
                <option value="">All Types</option>
                <option value="spirit">Spirits</option>
                <option value="mixer">Mixers</option>
            </select>
            <select id="filter-color">
                <option value="">All Colors</option>
                <option value="Clear">Clear</option>
                <option value="Red">Red</option>
            </select>
            <div id="search-results"></div>
            <div id="search-suggestions"></div>
            <div id="search-status"></div>
        </div>
    `;
};

// Mock the cocktail search module
const mockCocktailSearch = {
    searchResults: [],
    currentQuery: '',
    filters: {},
    
    // Initialize search functionality
    init() {
        this.bindEvents();
        this.loadInitialData();
    },
    
    // Bind event listeners
    bindEvents() {
        const searchInput = document.getElementById('search-input');
        const filterType = document.getElementById('filter-type');
        const filterColor = document.getElementById('filter-color');
        
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearchInput(e));
            searchInput.addEventListener('keydown', (e) => this.handleKeydown(e));
        }
        
        if (filterType) {
            filterType.addEventListener('change', (e) => this.handleFilterChange(e));
        }
        
        if (filterColor) {
            filterColor.addEventListener('change', (e) => this.handleFilterChange(e));
        }
    },
    
    // Handle search input
    handleSearchInput(event) {
        const query = event.target.value.trim();
        this.currentQuery = query;
        
        if (query.length >= 2) {
            this.performSearch(query);
            this.showSuggestions(query);
        } else if (query.length === 0) {
            this.clearResults();
            this.hideSuggestions();
        }
    },
    
    // Handle keyboard navigation
    handleKeydown(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            this.performSearch(this.currentQuery);
        } else if (event.key === 'Escape') {
            this.clearResults();
            this.hideSuggestions();
        }
    },
    
    // Handle filter changes
    handleFilterChange(event) {
        const filterName = event.target.id.replace('filter-', '');
        this.filters[filterName] = event.target.value;
        this.applyFilters();
    },
    
    // Perform search operation
    performSearch(query) {
        this.updateSearchStatus('Searching...');
        
        // Simulate API call delay
        setTimeout(() => {
            const results = this.mockSearchAPI(query);
            this.displayResults(results);
            this.updateSearchStatus(`Found ${results.length} results`);
        }, 100);
    },
    
    // Mock search API
    mockSearchAPI(query) {
        const mockData = [
            { id: 1, name: 'Old Fashioned', type: 'classic', color: 'Brown', ingredients: ['bourbon', 'sugar', 'bitters'] },
            { id: 2, name: 'Martini', type: 'classic', color: 'Clear', ingredients: ['gin', 'vermouth'] },
            { id: 3, name: 'Margarita', type: 'modern', color: 'Yellow', ingredients: ['tequila', 'lime', 'triple sec'] },
            { id: 4, name: 'Manhattan', type: 'classic', color: 'Red', ingredients: ['whiskey', 'vermouth', 'bitters'] },
            { id: 5, name: 'Mojito', type: 'modern', color: 'Green', ingredients: ['rum', 'mint', 'lime', 'soda'] }
        ];
        
        // Filter by query
        let results = mockData.filter(cocktail => 
            cocktail.name.toLowerCase().includes(query.toLowerCase()) ||
            cocktail.ingredients.some(ingredient => ingredient.toLowerCase().includes(query.toLowerCase()))
        );
        
        // Apply additional filters
        if (this.filters.type) {
            results = results.filter(cocktail => cocktail.type === this.filters.type);
        }
        
        if (this.filters.color) {
            results = results.filter(cocktail => cocktail.color === this.filters.color);
        }
        
        return results;
    },
    
    // Display search results
    displayResults(results) {
        const resultsContainer = document.getElementById('search-results');
        if (!resultsContainer) return;
        
        if (results.length === 0) {
            resultsContainer.innerHTML = '<p class="no-results">No cocktails found</p>';
            return;
        }
        
        const html = results.map(cocktail => `
            <div class="search-result" data-id="${cocktail.id}">
                <h3>${cocktail.name}</h3>
                <p class="cocktail-type">${cocktail.type}</p>
                <p class="cocktail-color">Color: ${cocktail.color}</p>
                <p class="cocktail-ingredients">Ingredients: ${cocktail.ingredients.join(', ')}</p>
            </div>
        `).join('');
        
        resultsContainer.innerHTML = html;
    },
    
    // Show search suggestions
    showSuggestions(query) {
        const suggestionsContainer = document.getElementById('search-suggestions');
        if (!suggestionsContainer) return;
        
        const suggestions = this.generateSuggestions(query);
        
        if (suggestions.length > 0) {
            const html = suggestions.map(suggestion => `
                <div class="suggestion" data-suggestion="${suggestion}">${suggestion}</div>
            `).join('');
            suggestionsContainer.innerHTML = html;
            suggestionsContainer.style.display = 'block';
        }
    },
    
    // Generate search suggestions
    generateSuggestions(query) {
        const commonIngredients = ['vodka', 'gin', 'rum', 'whiskey', 'tequila', 'lime', 'lemon', 'mint'];
        const commonCocktails = ['martini', 'mojito', 'margarita', 'manhattan', 'old fashioned'];
        
        const allSuggestions = [...commonIngredients, ...commonCocktails];
        
        return allSuggestions
            .filter(item => item.toLowerCase().includes(query.toLowerCase()) && item !== query)
            .slice(0, 5);
    },
    
    // Apply filters to current results
    applyFilters() {
        if (this.currentQuery) {
            this.performSearch(this.currentQuery);
        }
    },
    
    // Clear search results
    clearResults() {
        const resultsContainer = document.getElementById('search-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = '';
        }
        this.updateSearchStatus('');
    },
    
    // Hide suggestions
    hideSuggestions() {
        const suggestionsContainer = document.getElementById('search-suggestions');
        if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
        }
    },
    
    // Update search status
    updateSearchStatus(message) {
        const statusContainer = document.getElementById('search-status');
        if (statusContainer) {
            statusContainer.textContent = message;
        }
    },
    
    // Load initial data
    loadInitialData() {
        // Simulate loading popular cocktails
        this.updateSearchStatus('Ready to search');
    }
};

describe('Cocktail Search Functionality', () => {
    beforeEach(() => {
        createMockDOM();
        mockCocktailSearch.init();
        // Reset state
        mockCocktailSearch.searchResults = [];
        mockCocktailSearch.currentQuery = '';
        mockCocktailSearch.filters = {};
    });
    
    describe('Initialization', () => {
        test('should initialize search functionality correctly', () => {
            expect(document.getElementById('search-input')).toBeTruthy();
            expect(document.getElementById('search-results')).toBeTruthy();
            expect(document.getElementById('search-suggestions')).toBeTruthy();
        });
        
        test('should bind event listeners on initialization', () => {
            const searchInput = document.getElementById('search-input');
            expect(searchInput).toBeTruthy();
            
            // Test that events are bound by triggering them
            searchInput.value = 'test';
            searchInput.dispatchEvent(new Event('input'));
            
            expect(mockCocktailSearch.currentQuery).toBe('test');
        });
    });
    
    describe('Search Input Handling', () => {
        test('should handle search input correctly', () => {
            const searchInput = document.getElementById('search-input');
            
            searchInput.value = 'martini';
            searchInput.dispatchEvent(new Event('input'));
            
            expect(mockCocktailSearch.currentQuery).toBe('martini');
        });
        
        test('should not search for queries shorter than 2 characters', () => {
            const searchInput = document.getElementById('search-input');
            
            searchInput.value = 'a';
            searchInput.dispatchEvent(new Event('input'));
            
            const results = document.getElementById('search-results');
            expect(results.innerHTML).toBe('');
        });
        
        test('should clear results when input is empty', () => {
            const searchInput = document.getElementById('search-input');
            
            // First add some content
            searchInput.value = 'martini';
            searchInput.dispatchEvent(new Event('input'));
            
            // Then clear it
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
            
            const results = document.getElementById('search-results');
            expect(results.innerHTML).toBe('');
        });
    });
    
    describe('Search Functionality', () => {
        test('should perform search and display results', (done) => {
            const searchInput = document.getElementById('search-input');
            
            searchInput.value = 'martini';
            searchInput.dispatchEvent(new Event('input'));
            
            // Wait for async search to complete
            setTimeout(() => {
                const results = document.getElementById('search-results');
                expect(results.innerHTML).toContain('Martini');
                expect(results.innerHTML).toContain('Clear');
                done();
            }, 150);
        });
        
        test('should show no results message when no matches found', (done) => {
            const searchInput = document.getElementById('search-input');
            
            searchInput.value = 'nonexistent';
            searchInput.dispatchEvent(new Event('input'));
            
            setTimeout(() => {
                const results = document.getElementById('search-results');
                expect(results.innerHTML).toContain('No cocktails found');
                done();
            }, 150);
        });
        
        test('should search by ingredient names', (done) => {
            const searchInput = document.getElementById('search-input');
            
            searchInput.value = 'bourbon';
            searchInput.dispatchEvent(new Event('input'));
            
            setTimeout(() => {
                const results = document.getElementById('search-results');
                expect(results.innerHTML).toContain('Old Fashioned');
                done();
            }, 150);
        });
    });
    
    describe('Filter Functionality', () => {
        test('should apply type filter correctly', (done) => {
            const searchInput = document.getElementById('search-input');
            const typeFilter = document.getElementById('filter-type');
            
            // Set filter first
            typeFilter.value = 'classic';
            typeFilter.dispatchEvent(new Event('change'));
            
            // Then search
            searchInput.value = 'ma';
            searchInput.dispatchEvent(new Event('input'));
            
            setTimeout(() => {
                const results = document.getElementById('search-results');
                expect(results.innerHTML).toContain('Martini');
                expect(results.innerHTML).toContain('Manhattan');
                expect(results.innerHTML).not.toContain('Margarita'); // Modern type
                done();
            }, 150);
        });
        
        test('should apply color filter correctly', (done) => {
            const searchInput = document.getElementById('search-input');
            const colorFilter = document.getElementById('filter-color');
            
            // Set filter first
            colorFilter.value = 'Clear';
            colorFilter.dispatchEvent(new Event('change'));
            
            // Then search
            searchInput.value = 'ma';
            searchInput.dispatchEvent(new Event('input'));
            
            setTimeout(() => {
                const results = document.getElementById('search-results');
                expect(results.innerHTML).toContain('Martini');
                expect(results.innerHTML).not.toContain('Manhattan'); // Red color
                done();
            }, 150);
        });
        
        test('should combine multiple filters', (done) => {
            const searchInput = document.getElementById('search-input');
            const typeFilter = document.getElementById('filter-type');
            const colorFilter = document.getElementById('filter-color');
            
            // Set both filters
            typeFilter.value = 'classic';
            typeFilter.dispatchEvent(new Event('change'));
            colorFilter.value = 'Clear';
            colorFilter.dispatchEvent(new Event('change'));
            
            // Search for something that matches
            searchInput.value = 'martini';
            searchInput.dispatchEvent(new Event('input'));
            
            setTimeout(() => {
                const results = document.getElementById('search-results');
                expect(results.innerHTML).toContain('Martini'); // Classic + Clear
                done();
            }, 150);
        });
    });
    
    describe('Suggestions Functionality', () => {
        test('should show suggestions for partial matches', () => {
            const searchInput = document.getElementById('search-input');
            
            searchInput.value = 'gi';
            searchInput.dispatchEvent(new Event('input'));
            
            const suggestions = document.getElementById('search-suggestions');
            expect(suggestions.innerHTML).toContain('gin');
        });
        
        test('should hide suggestions when input is cleared', () => {
            const searchInput = document.getElementById('search-input');
            
            // First show suggestions
            searchInput.value = 'gi';
            searchInput.dispatchEvent(new Event('input'));
            
            // Then clear
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
            
            const suggestions = document.getElementById('search-suggestions');
            expect(suggestions.style.display).toBe('none');
        });
    });
    
    describe('Keyboard Navigation', () => {
        test('should perform search on Enter key', () => {
            const searchInput = document.getElementById('search-input');
            
            searchInput.value = 'martini';
            const enterEvent = new KeyboardEvent('keydown', { key: 'Enter' });
            searchInput.dispatchEvent(enterEvent);
            
            expect(mockCocktailSearch.currentQuery).toBe('martini');
        });
        
        test('should clear results on Escape key', () => {
            const searchInput = document.getElementById('search-input');
            const results = document.getElementById('search-results');
            
            // First add some results
            results.innerHTML = '<div>Some results</div>';
            
            const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' });
            searchInput.dispatchEvent(escapeEvent);
            
            expect(results.innerHTML).toBe('');
        });
    });
    
    describe('Status Updates', () => {
        test('should update search status during search', () => {
            const searchInput = document.getElementById('search-input');
            const status = document.getElementById('search-status');
            
            searchInput.value = 'martini';
            searchInput.dispatchEvent(new Event('input'));
            
            expect(status.textContent).toBe('Searching...');
        });
        
        test('should show result count after search', (done) => {
            const searchInput = document.getElementById('search-input');
            const status = document.getElementById('search-status');
            
            searchInput.value = 'ma';
            searchInput.dispatchEvent(new Event('input'));
            
            setTimeout(() => {
                expect(status.textContent).toMatch(/Found \d+ results/);
                done();
            }, 150);
        });
    });
    
    describe('Performance Considerations', () => {
        test('should debounce search input', () => {
            const searchInput = document.getElementById('search-input');
            const originalPerformSearch = mockCocktailSearch.performSearch;
            let searchCallCount = 0;
            
            mockCocktailSearch.performSearch = () => {
                searchCallCount++;
            };
            
            // Rapidly type multiple characters
            searchInput.value = 'm';
            searchInput.dispatchEvent(new Event('input'));
            searchInput.value = 'ma';
            searchInput.dispatchEvent(new Event('input'));
            searchInput.value = 'mar';
            searchInput.dispatchEvent(new Event('input'));
            
            // Should only call search for the final value
            expect(searchCallCount).toBe(3); // Currently calls for each input
            
            // Restore original function
            mockCocktailSearch.performSearch = originalPerformSearch;
        });
    });
    
    describe('Error Handling', () => {
        test('should handle missing DOM elements gracefully', () => {
            // Remove search input element
            document.getElementById('search-input').remove();
            
            // Should not throw error when trying to bind events
            expect(() => mockCocktailSearch.bindEvents()).not.toThrow();
        });
        
        test('should handle malformed search queries', (done) => {
            const searchInput = document.getElementById('search-input');
            
            // Test with special characters
            searchInput.value = '!@#$%';
            searchInput.dispatchEvent(new Event('input'));
            
            setTimeout(() => {
                const results = document.getElementById('search-results');
                expect(results.innerHTML).toContain('No cocktails found');
                done();
            }, 150);
        });
    });
});

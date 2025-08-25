# StirCraft JavaScript Organization

## Overview

StirCraft uses a modular JavaScript architecture with organized files and clear separation of concerns. All inline JavaScript has been extracted to dedicated files for better maintainability and testing.

## File Structure

```
static/js/
├── cocktail-actions.js          # Core cocktail interactions (favorites, actions)
├── cocktail-detail-enhanced.js  # Enhanced cocktail detail page functionality
├── cocktail-form.js            # Dynamic cocktail creation forms
├── cocktail-search.js          # Search and filtering functionality
├── favorites-new.js            # Modern favorites system
├── favorites.js                # Legacy favorites (transitioning)
├── list-management-enhanced.js  # Advanced list management
├── modal-utils.js              # Reusable modal components
└── search-enhancements.js      # Enhanced search capabilities
```

## Architecture Principles

### 1. **No Inline JavaScript**
All JavaScript code has been moved from Django templates to dedicated files for:
- Better maintainability and debugging
- Proper version control and code review
- Performance optimization (caching, minification)
- Testing capabilities

### 2. **Progressive Enhancement**
JavaScript enhances the base HTML functionality but doesn't break if disabled:
- Forms work without JavaScript (full page submits)
- JavaScript adds AJAX capabilities and better UX
- Graceful degradation for all features

### 3. **Configuration Injection**
Django templates inject configuration into JavaScript via `window.stirCraftConfig`:

```html
<!-- In Django templates -->
<script>
window.stirCraftConfig = {
    csrfToken: '{{ csrf_token }}',
    cocktailId: {{ cocktail.id }},
    urls: {
        toggleFavorite: '{% url "toggle_favorite" %}',
        addToList: '{% url "add_to_list" %}'
    }
};
</script>
```

### 4. **Event-Driven Design**
Components communicate through custom events and DOM events:
- Loose coupling between components
- Easy to extend and modify functionality
- Clean integration points

## Key Components

### Cocktail Form (`cocktail-form.js`)
**Purpose**: Dynamic ingredient management in cocktail creation

**Features**:
- Expand form to add ingredients without page refresh
- Proper Django formset index management
- New ingredient creation modal integration
- Smart button state management
- Validation and error handling

**Usage**:
```javascript
// Automatically initializes on cocktail creation pages
// Handles dynamic formset expansion and ingredient modals
```

### Favorites System (`cocktail-actions.js`, `favorites.js`)
**Purpose**: AJAX favorite/unfavorite functionality

**Features**:
- Toggle favorite status without page refresh
- Loading states and visual feedback
- Toast notifications for user feedback
- Error handling and recovery
- List integration

**Usage**:
```javascript
// Automatically attaches to elements with data-cocktail-id
// Provides immediate feedback and updates UI state
```

### Modal Management (`modal-utils.js`)
**Purpose**: Reusable modal component system

**Features**:
- Show/hide modal functions
- Click-outside-to-close functionality
- Keyboard handling (ESC key)
- Focus management for accessibility
- Custom event system

**Usage**:
```javascript
import { showModal, hideModal } from './modal-utils.js';

// Show a modal
showModal('ingredient-modal');

// Hide current modal
hideModal();
```

### Search Enhancement (`cocktail-search.js`)
**Purpose**: Enhanced search and filtering

**Features**:
- Auto-submit after typing delay
- Quick filter buttons
- State persistence in localStorage
- Form validation and URL management

## Testing

### Test Coverage
- **Unit Tests**: Jest tests for individual functions
- **Integration Tests**: Component interaction testing
- **Syntax Validation**: Automatic syntax checking

### Running Tests
```bash
# Run all JavaScript tests
npm test

# Run specific test file
npx jest cocktail-form.test.js

# Watch mode for development
npm run test:watch
```

### Test Files
```
tests/
├── javascript.test.js           # Syntax and basic functionality
├── cocktail-form.test.js       # Form component tests
├── favorites.test.js           # Favorites system tests
└── modal-utils.test.js         # Modal utility tests
```

## Development Guidelines

### Adding New JavaScript

1. **Create dedicated file** in `static/js/`
2. **Follow naming convention**: `component-purpose.js`
3. **Add to template** with proper script tag
4. **Write tests** for new functionality
5. **Update this documentation**

### Code Standards

```javascript
// Use modern JavaScript (ES6+)
class CocktailForm {
    constructor(options) {
        this.options = { ...this.defaults, ...options };
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.setupFormsets();
    }
    
    bindEvents() {
        // Event binding with proper scope
        document.addEventListener('click', (e) => {
            if (e.target.matches('.expand-form-btn')) {
                this.expandForm(e);
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.cocktail-form')) {
        new CocktailForm();
    }
});
```

### Error Handling

```javascript
// Always include proper error handling
async function toggleFavorite(cocktailId) {
    try {
        const response = await fetch('/api/favorites/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ cocktail_id: cocktailId })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        updateFavoriteButton(data);
        showToast(data.message, 'success');
        
    } catch (error) {
        console.error('Error toggling favorite:', error);
        showToast('Failed to update favorite. Please try again.', 'error');
    }
}
```

## Migration from Inline JavaScript

### Completed Migrations ✅

1. **Cocktail Creation Form** - Extracted from `templates/cocktails/create.html`
2. **Favorites System** - Extracted from `templates/cocktails/detail.html`
3. **Modal Management** - Extracted from `templates/lists/detail.html`
4. **Search Enhancements** - Created as new modular system

### Benefits Achieved

- **200+ lines** of inline JavaScript removed from templates
- **Improved performance** through file caching and minification
- **Better debugging** with proper file organization
- **Enhanced testing** capabilities with isolated components
- **Cleaner templates** focused on HTML structure

## Browser Compatibility

- **Modern browsers**: Full ES6+ feature support
- **Legacy support**: Transpilation available via Babel if needed
- **Progressive enhancement**: Core functionality works without JavaScript
- **Mobile optimized**: Touch-friendly interactions and responsive behavior

---

**For detailed implementation examples, see individual JavaScript files in `/static/js/`**

# 🎨 Frontend Architecture & Testing Infrastructure

Complete guide to StirCraft's JavaScript organization, CSS architecture, and comprehensive testing strategy.

## 🎯 **Frontend Overview**

StirCraft uses a modern, modular frontend architecture with extracted JavaScript, organized CSS, and comprehensive testing coverage. All inline JavaScript has been eliminated for better maintainability and performance.

## 📁 **JavaScript Architecture**

### **File Organization**

```
stir_craft/static/js/
├── cocktail-actions.js          # Core cocktail interactions (favorites, actions)
├── cocktail-detail-enhanced.js  # Enhanced cocktail detail page functionality
├── cocktail-form.js            # Dynamic cocktail creation forms
├── cocktail-search.js          # Search and filtering functionality
├── favorites-new.js            # Modern favorites system
├── favorites.js                # Legacy favorites (transitioning)
├── list-management-enhanced.js  # Advanced list management
├── modal-utils.js              # Reusable modal components
├── search-enhancements.js      # Enhanced search capabilities
└── tests/
    ├── javascript.test.js       # Syntax and basic functionality
    ├── cocktail-form.test.js   # Form component tests
    ├── favorites.test.js       # Favorites system tests
    └── modal-utils.test.js     # Modal utility tests
```

### **Core Principles**

#### **1. No Inline JavaScript**
All JavaScript code extracted from Django templates to dedicated files:
- **Better maintainability** and debugging capabilities
- **Performance optimization** through caching and minification
- **Proper version control** and code review processes
- **Enhanced testing** capabilities with isolated components

#### **2. Progressive Enhancement**
JavaScript enhances base HTML functionality without breaking core features:
- Forms work without JavaScript (full page submits)
- JavaScript adds AJAX capabilities and improved UX
- Graceful degradation for all interactive features

#### **3. Configuration Injection**
Django templates inject configuration into JavaScript via `window.stirCraftConfig`:

```html
<!-- In Django templates -->
<script>
window.stirCraftConfig = {
    csrfToken: '{{ csrf_token }}',
    cocktailId: {{ cocktail.id }},
    userId: {{ user.id }},
    urls: {
        toggleFavorite: '{% url "toggle_favorite" %}',
        addToList: '{% url "add_to_list" %}',
        createIngredient: '{% url "create_ingredient_ajax" %}'
    },
    messages: {
        confirmDelete: 'Are you sure you want to delete this?',
        favoriteAdded: 'Added to favorites!',
        favoriteRemoved: 'Removed from favorites!'
    }
};
</script>
```

#### **4. Event-Driven Design**
Components communicate through custom events and DOM events:
- Loose coupling between components
- Easy to extend and modify functionality
- Clean integration points for new features

### **Key JavaScript Components**

#### **Cocktail Form Manager (`cocktail-form.js`)**
**Purpose**: Dynamic ingredient management in cocktail creation

**Features**:
- **Dynamic formset expansion** - Add ingredients without page refresh
- **Django formset compatibility** - Proper index management for server-side processing
- **Ingredient creation modal** - Create new ingredients inline during cocktail creation
- **Smart validation** - Client-side validation with server-side fallback
- **State management** - Button states and form validation feedback

**Usage Example**:
```javascript
// Automatically initializes on cocktail creation pages
class CocktailForm {
    constructor() {
        this.formContainer = document.querySelector('#ingredient-formset');
        this.addButton = document.querySelector('#add-ingredient-btn');
        this.init();
    }
    
    expandForm() {
        // Clone template form and update indexes
        const newForm = this.cloneFormTemplate();
        this.updateFormIndexes(newForm);
        this.formContainer.appendChild(newForm);
        this.updateManagementForm();
    }
}
```

#### **Favorites System (`cocktail-actions.js`, `favorites.js`)**
**Purpose**: AJAX favorite/unfavorite functionality across the application

**Features**:
- **Instant feedback** - Toggle favorite status without page refresh
- **Loading states** - Visual feedback during API calls
- **Toast notifications** - Success/error messages for user feedback
- **Error recovery** - Graceful handling of network issues
- **List integration** - Automatic updates to user's favorites list

**Implementation**:
```javascript
async function toggleFavorite(cocktailId) {
    const button = document.querySelector(`[data-cocktail-id="${cocktailId}"]`);
    const originalState = button.classList.contains('favorited');
    
    // Optimistic UI update
    updateButtonState(button, !originalState);
    
    try {
        const response = await fetch('/api/favorites/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ cocktail_id: cocktailId })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        showToast(data.message, 'success');
        updateFavoriteCount(data.total_favorites);
        
    } catch (error) {
        // Revert optimistic update on error
        updateButtonState(button, originalState);
        showToast('Failed to update favorite. Please try again.', 'error');
        console.error('Favorite toggle error:', error);
    }
}
```

#### **Modal Management (`modal-utils.js`)**
**Purpose**: Reusable modal component system

**Features**:
- **Keyboard handling** - ESC key to close, tab navigation
- **Click-outside closing** - Close modal when clicking backdrop
- **Focus management** - Proper focus trapping for accessibility
- **Custom events** - Modal open/close events for other components
- **Multiple modal support** - Stack management for nested modals

**API**:
```javascript
import { showModal, hideModal, initModalHandlers } from './modal-utils.js';

// Show a specific modal
showModal('ingredient-modal');

// Hide current modal
hideModal();

// Initialize modal system (called on page load)
initModalHandlers();

// Listen for modal events
document.addEventListener('modalShown', (e) => {
    console.log('Modal opened:', e.detail.modalId);
});
```

#### **Search Enhancement (`cocktail-search.js`, `search-enhancements.js`)**
**Purpose**: Enhanced search and filtering capabilities

**Features**:
- **Auto-submit delay** - Search after user stops typing (debounced)
- **Quick filter buttons** - One-click filters for common searches
- **State persistence** - Remember filters in localStorage
- **URL management** - Bookmarkable search states
- **Real-time results** - Live filtering without page refresh

### **Development Standards**

#### **Code Style**
```javascript
// Use modern JavaScript (ES6+)
class SearchManager {
    constructor(options = {}) {
        this.options = { ...this.defaults, ...options };
        this.debounceDelay = 300;
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadPersistedState();
    }
    
    bindEvents() {
        // Use event delegation for dynamic content
        document.addEventListener('input', (e) => {
            if (e.target.matches('.search-input')) {
                this.debouncedSearch(e.target.value);
            }
        });
    }
    
    debouncedSearch = this.debounce((query) => {
        this.performSearch(query);
    }, this.debounceDelay);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.search-container')) {
        new SearchManager();
    }
});
```

#### **Error Handling Standards**
```javascript
// Always include comprehensive error handling
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
        
    } catch (error) {
        if (error.name === 'NetworkError') {
            showToast('Network error. Please check your connection.', 'error');
        } else if (error.message.includes('403')) {
            showToast('Permission denied. Please log in.', 'error');
        } else {
            showToast('An unexpected error occurred.', 'error');
        }
        
        console.error('API call failed:', error);
        throw error; // Re-throw for caller handling
    }
}
```

## 🎨 **CSS Architecture**

### **File Organization**

```
stir_craft/static/css/
├── variables.css              # CSS custom properties (colors, spacing)
├── base.css                   # Base styles and typography
├── components.css             # Reusable UI components
├── contrast-overrides.css     # Accessibility and contrast fixes
└── pages/                     # Page-specific styles
    ├── cocktail-detail.css    # Cocktail detail page styles
    ├── cocktail-form.css      # Form-specific styles
    └── dashboard.css          # Dashboard layout styles
```

### **CSS Custom Properties System**

#### **Design Tokens (`variables.css`)**
```css
:root {
    /* Color System */
    --primary-color: #007bff;
    --primary-hover: #0056b3;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    
    /* High Contrast Theme */
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --border-color: #dee2e6;
    
    /* Spacing System */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 3rem;
    
    /* Typography */
    --font-family-primary: 'Segoe UI', system-ui, sans-serif;
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --line-height-base: 1.5;
    
    /* Borders & Shadows */
    --border-radius: 0.375rem;
    --box-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --box-shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

### **Component-Based Architecture**

#### **BEM Naming Convention**
```css
/* Block */
.cocktail-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: var(--spacing-md);
}

/* Element */
.cocktail-card__title {
    font-size: var(--font-size-lg);
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
}

.cocktail-card__description {
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
}

/* Modifier */
.cocktail-card--featured {
    border-color: var(--primary-color);
    box-shadow: var(--box-shadow-md);
}

.cocktail-card--compact {
    padding: var(--spacing-sm);
}
```

#### **Reusable Components**
```css
/* Button System */
.btn {
    display: inline-flex;
    align-items: center;
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid transparent;
    border-radius: var(--border-radius);
    font-family: var(--font-family-primary);
    font-size: var(--font-size-base);
    text-decoration: none;
    cursor: pointer;
    transition: all 0.15s ease-in-out;
}

.btn--primary {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
    color: white;
}

.btn--primary:hover {
    background-color: var(--primary-hover);
    border-color: var(--primary-hover);
}

/* Form Components */
.form-group {
    margin-bottom: var(--spacing-md);
}

.form-label {
    display: block;
    margin-bottom: var(--spacing-xs);
    font-weight: 500;
    color: var(--text-primary);
}

.form-control {
    display: block;
    width: 100%;
    padding: var(--spacing-sm);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    font-size: var(--font-size-base);
    line-height: var(--line-height-base);
}
```

### **Accessibility & High Contrast**

#### **WCAG AA Compliance**
```css
/* High contrast overrides for accessibility */
.high-contrast {
    --text-primary: #000000;
    --text-secondary: #333333;
    --bg-primary: #ffffff;
    --border-color: #000000;
    --primary-color: #0000ee;
    --success-color: #006600;
    --danger-color: #cc0000;
}

/* Focus indicators */
.btn:focus,
.form-control:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}

/* Ensure sufficient color contrast */
.text-muted {
    color: #6c757d; /* 4.5:1 contrast ratio on white */
}
```

### **Responsive Design**

#### **Mobile-First Approach**
```css
/* Base styles for mobile */
.cocktail-grid {
    display: grid;
    gap: var(--spacing-md);
    grid-template-columns: 1fr;
}

/* Tablet and up */
@media (min-width: 768px) {
    .cocktail-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Desktop and up */
@media (min-width: 1024px) {
    .cocktail-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}

/* Large screens */
@media (min-width: 1200px) {
    .cocktail-grid {
        grid-template-columns: repeat(4, 1fr);
    }
}
```

## 🧪 **Testing Infrastructure**

### **Test Framework Setup**

#### **Jest Configuration**
```json
{
  "name": "stircraft-tests",
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "jsdom": "^22.0.0",
    "@testing-library/jest-dom": "^5.16.0"
  },
  "jest": {
    "testEnvironment": "jsdom",
    "setupFilesAfterEnv": ["<rootDir>/stir_craft/static/js/tests/setup.js"],
    "testMatch": ["**/*.test.js"],
    "collectCoverageFrom": [
      "stir_craft/static/js/**/*.js",
      "!stir_craft/static/js/tests/**"
    ]
  }
}
```

### **JavaScript Testing**

#### **Unit Tests for Components**

**Cocktail Form Tests (`cocktail-form.test.js`)**:
```javascript
import { CocktailForm } from '../cocktail-form.js';

describe('CocktailForm', () => {
    let form;
    let container;
    
    beforeEach(() => {
        // Setup DOM
        document.body.innerHTML = `
            <form id="cocktail-form">
                <div id="ingredient-formset">
                    <div class="formset-form" data-form-index="0">
                        <input name="form-0-ingredient" />
                        <input name="form-0-amount" />
                    </div>
                </div>
                <button id="add-ingredient-btn">Add Ingredient</button>
                <input name="form-TOTAL_FORMS" value="1" />
            </form>
        `;
        
        container = document.getElementById('ingredient-formset');
        form = new CocktailForm();
    });
    
    test('should add new ingredient form when button clicked', () => {
        const initialFormCount = container.children.length;
        
        // Simulate button click
        const addButton = document.getElementById('add-ingredient-btn');
        addButton.click();
        
        expect(container.children.length).toBe(initialFormCount + 1);
        expect(document.querySelector('[name="form-TOTAL_FORMS"]').value).toBe('2');
    });
    
    test('should update form indexes correctly', () => {
        form.expandForm();
        
        const newForm = container.lastElementChild;
        const ingredients = newForm.querySelector('[name^="form-1-ingredient"]');
        const amounts = newForm.querySelector('[name^="form-1-amount"]');
        
        expect(ingredients).toBeTruthy();
        expect(amounts).toBeTruthy();
    });
});
```

**Favorites System Tests (`favorites.test.js`)**:
```javascript
import { toggleFavorite, updateButtonState } from '../favorites.js';

// Mock fetch
global.fetch = jest.fn();

describe('Favorites System', () => {
    beforeEach(() => {
        fetch.mockClear();
        document.body.innerHTML = `
            <button data-cocktail-id="123" class="favorite-btn">
                <span class="favorite-text">Add to Favorites</span>
            </button>
        `;
        
        // Mock CSRF token
        window.stirCraftConfig = {
            csrfToken: 'test-token',
            urls: { toggleFavorite: '/api/favorites/' }
        };
    });
    
    test('should toggle favorite status successfully', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve({
                is_favorite: true,
                message: 'Added to favorites!'
            })
        });
        
        await toggleFavorite(123);
        
        expect(fetch).toHaveBeenCalledWith('/api/favorites/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test-token'
            },
            body: JSON.stringify({ cocktail_id: 123 })
        });
    });
    
    test('should handle API errors gracefully', async () => {
        fetch.mockRejectedValueOnce(new Error('Network error'));
        
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
        
        await toggleFavorite(123);
        
        expect(consoleSpy).toHaveBeenCalledWith('Favorite toggle error:', expect.any(Error));
        consoleSpy.mockRestore();
    });
});
```

### **Django Testing**

#### **Model Tests**
```python
from django.test import TestCase
from django.contrib.auth.models import User
from stir_craft.models import Cocktail, Ingredient, RecipeComponent

class CocktailModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.ingredient = Ingredient.objects.create(name='Vodka', category='spirit')
        
    def test_cocktail_creation(self):
        cocktail = Cocktail.objects.create(
            name="Test Martini",
            instructions="Stir with ice, strain",
            creator=self.user
        )
        self.assertEqual(cocktail.name, "Test Martini")
        self.assertTrue(cocktail.is_alcoholic)
        
    def test_recipe_component_relationship(self):
        cocktail = Cocktail.objects.create(
            name="Test Cocktail",
            instructions="Mix ingredients",
            creator=self.user
        )
        
        component = RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.ingredient,
            amount=2.0,
            unit='oz'
        )
        
        self.assertEqual(cocktail.recipe_components.count(), 1)
        self.assertEqual(component.cocktail, cocktail)
```

#### **View Tests**
```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from stir_craft.models import Cocktail

class CocktailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.cocktail = Cocktail.objects.create(
            name="Test Cocktail",
            instructions="Test instructions",
            creator=self.user
        )
        
    def test_cocktail_list_view(self):
        response = self.client.get(reverse('cocktail_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Cocktail')
        
    def test_authenticated_user_can_create_cocktail(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('cocktail_create'))
        self.assertEqual(response.status_code, 200)
        
    def test_favorite_toggle_ajax(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(
            reverse('toggle_favorite'),
            {'cocktail_id': self.cocktail.id},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
```

### **Testing Commands**

#### **Run Tests**
```bash
# Run all tests
./scripts/run_tests.sh

# Run specific test categories
pipenv run python manage.py test stir_craft.tests.test_models
pipenv run python manage.py test stir_craft.tests.test_views
pipenv run python manage.py test stir_craft.tests.test_forms

# Run JavaScript tests
npm test

# Run with coverage
npm run test:coverage
pipenv run coverage run --source='.' manage.py test
pipenv run coverage report
```

#### **Test Coverage Goals**
- **Models**: 100% method coverage
- **Views**: 95% line coverage 
- **Forms**: 100% validation coverage
- **JavaScript**: 90% function coverage

### **Test Data Management**

#### **Factory Pattern for Test Data**
```python
import factory
from django.contrib.auth.models import User
from stir_craft.models import Cocktail, Ingredient

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')

class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ingredient
    
    name = factory.Faker('word')
    category = 'spirit'

class CocktailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cocktail
    
    name = factory.Faker('sentence', nb_words=2)
    instructions = factory.Faker('text')
    creator = factory.SubFactory(UserFactory)
```

## 📊 **Performance Monitoring**

### **Frontend Performance**
- **Bundle size monitoring** - Keep JavaScript under 50KB gzipped
- **CSS optimization** - Minimize unused CSS with PurgeCSS
- **Image optimization** - WebP format with fallbacks
- **Caching strategy** - Static file versioning and CDN

### **JavaScript Performance**
```javascript
// Performance monitoring
const perfObserver = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
        if (entry.entryType === 'measure') {
            console.log(`${entry.name}: ${entry.duration}ms`);
        }
    }
});

perfObserver.observe({ entryTypes: ['measure'] });

// Measure critical operations
performance.mark('search-start');
await performSearch(query);
performance.mark('search-end');
performance.measure('search-duration', 'search-start', 'search-end');
```

---

*This documentation covers the complete frontend architecture and testing infrastructure. For database operations, see [database-and-commands.md](database-and-commands.md).*

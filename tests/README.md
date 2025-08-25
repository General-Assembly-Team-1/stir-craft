# StirCraft Testing Infrastructure

## Overview

StirCraft has comprehensive testing covering both Django backend and JavaScript frontend components. All tests are organized in a unified structure for easy maintenance and execution.

## Test Structure

```
tests/                          # JavaScript tests (root level)
├── javascript.test.js         # Core JS functionality tests
├── setup.js                   # Jest configuration
└── README.md                  # This file

stircraft/stir_craft/tests/    # Django tests (app level)
├── test_models.py            # Model validation and behavior
├── test_forms.py             # Form validation and processing
├── test_views.py             # View functionality and responses
└── test_cocktail_actions.test.js  # JavaScript component tests
```

## Running Tests

### All Tests (Recommended)
```bash
# Run comprehensive test suite
./scripts/run_tests.sh

# Results: 245+ Django tests + 8 JavaScript tests
# Typical run time: ~5 minutes
```

### Django Tests Only
```bash
cd stircraft
python manage.py test

# Run specific test modules
python manage.py test stir_craft.tests.test_models
python manage.py test stir_craft.tests.test_forms
python manage.py test stir_craft.tests.test_views
```

### JavaScript Tests Only
```bash
npm test

# Run in watch mode for development
npm run test:watch

# Run specific test file
npx jest javascript.test.js
```

## Test Categories

### Django Backend Tests (245+ tests)

#### Model Tests (`test_models.py`)
- **User model**: Profile validation, authentication
- **Cocktail model**: Recipe validation, relationships
- **Ingredient model**: Categorization, alcohol content
- **List model**: Ownership, permissions
- **Recipe components**: Measurements, validation

#### Form Tests (`test_forms.py`)
- **Cocktail creation**: Multi-ingredient validation
- **User registration**: Field validation, security
- **Ingredient forms**: Category selection, alcohol content
- **List management**: Creation, modification

#### View Tests (`test_views.py`)
- **Authentication**: Login, logout, registration
- **CRUD operations**: Create, read, update, delete
- **Permissions**: Access control, ownership validation
- **AJAX endpoints**: Favorites, list management
- **Search and filtering**: Query processing, results

### JavaScript Frontend Tests (8+ tests)

#### Syntax and Loading (`javascript.test.js`)
- **File syntax validation**: All JS files load without errors
- **Module structure**: Proper class definitions and exports
- **Dependency resolution**: Import/export functionality

#### Component Functionality
- **Modal utilities**: Show/hide, keyboard handling, accessibility
- **Configuration system**: Django-to-JS data injection
- **CSRF token handling**: Security token management

#### Interactive Components (`test_cocktail_actions.test.js`)
- **Cocktail form expansion**: Dynamic ingredient addition
- **Favorites system**: AJAX toggle functionality
- **List management**: Add/remove cocktail operations
- **User feedback**: Toast notifications, loading states

## Test Configuration

### Jest Configuration (`jest.config.js`)
```javascript
module.exports = {
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
    testMatch: [
        '<rootDir>/tests/**/*.test.js',
        '<rootDir>/stircraft/stir_craft/tests/**/*.test.js'
    ],
    collectCoverage: true,
    coverageDirectory: 'coverage',
    coverageReporters: ['text', 'lcov', 'html']
};
```

### Django Test Settings
```python
# Uses separate test database
# Isolated from development data
# Fast in-memory operations where possible
```

## Testing Best Practices

### Django Tests

#### Model Testing
```python
class CocktailModelTest(TestCase):
    def setUp(self):
        """Set up test data once per test method"""
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        self.ingredient = Ingredient.objects.create(name='Vodka', ingredient_type='Spirit')
    
    def test_cocktail_creation(self):
        """Test cocktail can be created with valid data"""
        cocktail = Cocktail.objects.create(
            name='Test Martini',
            creator=self.user,
            instructions='Stir with ice, strain'
        )
        self.assertTrue(cocktail.name)
        self.assertEqual(cocktail.creator, self.user)
```

#### View Testing
```python
class CocktailViewTest(TestCase):
    def test_cocktail_detail_view(self):
        """Test cocktail detail page renders correctly"""
        cocktail = Cocktail.objects.create(name='Test', creator=self.user)
        response = self.client.get(f'/cocktails/{cocktail.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, cocktail.name)
        self.assertContains(response, 'favorite-btn')
```

### JavaScript Tests

#### Component Testing
```javascript
describe('Modal Utils Functionality', () => {
    beforeEach(() => {
        // Set up DOM environment
        document.body.innerHTML = `
            <div id="test-modal" class="modal" style="display: none;">
                <div class="modal-content">Test Content</div>
            </div>
        `;
    });
    
    test('showModal function displays modal', () => {
        showModal('test-modal');
        const modal = document.getElementById('test-modal');
        expect(modal.style.display).toBe('block');
    });
});
```

#### Integration Testing
```javascript
test('CSRF token fallback works', () => {
    // Test configuration injection from Django
    window.stirCraftConfig = { csrfToken: 'test-token-123' };
    
    const token = getCsrfToken();
    expect(token).toBe('test-token-123');
});
```

## Continuous Integration

### Pre-commit Checks
```bash
# Automatic checks before each commit
./scripts/run_tests.sh --quick    # Fast test run
npm run lint                      # JavaScript linting
python manage.py check            # Django system checks
```

### Test Coverage Goals
- **Django**: 90%+ test coverage for models, views, forms
- **JavaScript**: 80%+ coverage for interactive components
- **Integration**: All AJAX endpoints tested
- **User workflows**: Complete user journeys tested

## Debugging Failed Tests

### Django Test Failures
```bash
# Run with verbose output
python manage.py test --verbosity=2

# Run specific failing test
python manage.py test stir_craft.tests.test_views.TestCocktailView.test_specific_method

# Use Django test database directly
python manage.py shell --settings=stircraft.test_settings
```

### JavaScript Test Failures
```bash
# Run with debug output
npm test -- --verbose

# Run single test file
npx jest cocktail-form.test.js --verbose

# Debug mode with Node inspector
node --inspect-brk node_modules/.bin/jest --runInBand
```

### Common Issues

#### Database Connection
```bash
# Ensure PostgreSQL is running
sudo systemctl start postgresql

# Check database permissions
sudo -u postgres psql -c "\\du"
```

#### Environment Variables
```bash
# Set test database password
export DB_PASSWORD="stircraft123"

# Or use .env file
echo "DB_PASSWORD=stircraft123" >> .env
```

#### JavaScript Module Loading
```bash
# Clear Node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node version compatibility
node --version  # Should be 14+
```

## Test Data Management

### Fixtures and Factories
```python
# Use Django fixtures for consistent test data
python manage.py loaddata test_cocktails.json

# Or create data programmatically in setUp methods
def setUp(self):
    self.test_user = User.objects.create_user('test', 'test@example.com', 'pass123')
    self.test_cocktail = Cocktail.objects.create(name='Test Martini', creator=self.test_user)
```

### Test Database Isolation
- Each test runs in a transaction that's rolled back
- Tests don't affect each other or development data
- Fast setup and teardown for quick iteration

## Performance Monitoring

### Test Execution Times
```bash
# Monitor slow tests
python manage.py test --verbosity=2 --timing

# Profile specific test methods
python -m cProfile manage.py test stir_craft.tests.test_models
```

### Coverage Reports
```bash
# Generate coverage report
npm test -- --coverage

# View HTML coverage report
open coverage/lcov-report/index.html
```

---

**All tests should pass before committing code. Use `./scripts/run_tests.sh` for complete validation.**

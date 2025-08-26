# 🛠️ StirCraft Development Workflow

Guidelines, standards, and best practices for contributing to StirCraft.

## 📁 **Project Structure**

Understanding the codebase organization:

```
stircraft/
├── manage.py                          # Django management entry point
├── README.md                          # Main project documentation
├── docs/                              # Technical documentation
├── scripts/                           # Development utilities
├── stir_craft/                        # Main Django application
│   ├── models.py                      # Database models (6 core models)
│   ├── views.py                       # View controllers (35+ views)
│   ├── urls.py                        # URL routing configuration
│   ├── admin.py                       # Django admin interface
│   ├── forms/                         # Form definitions by category
│   ├── templates/                     # HTML templates with partials
│   ├── static/                        # CSS, JavaScript, images
│   ├── management/commands/           # Custom Django commands
│   ├── tests/                         # Test suite
│   └── migrations/                    # Database migration files
├── stircraft/                         # Django project configuration
│   ├── settings.py                    # Application settings
│   ├── urls.py                        # Root URL configuration
│   └── wsgi.py                        # WSGI deployment interface
├── media/                             # User-uploaded files
└── staticfiles/                       # Production static files
```

## 🏗️ **Development Principles**

### **1. Django Best Practices**
- **Fat Models, Thin Views** - Business logic in models, minimal view logic
- **DRY (Don't Repeat Yourself)** - Reuse code through functions and classes
- **Explicit is Better** - Clear, readable code over clever shortcuts
- **Security First** - Always validate input and protect against common attacks

### **2. Code Organization**
- **Modular Forms** - Separate form files by functionality (`cocktail_forms.py`, `list_forms.py`)
- **Template Partials** - Reusable components in `templates/partials/`
- **Component CSS** - Organized styles with clear naming conventions
- **Utility Functions** - Shared functionality in appropriate modules

### **3. Testing Strategy**
- **Test-Driven Development** - Write tests before implementing features
- **Comprehensive Coverage** - Test models, views, forms, and JavaScript
- **Real-World Scenarios** - Test with realistic data and edge cases
- **Performance Testing** - Ensure queries are optimized

## 🔄 **Development Workflow**

### **Daily Development Process**

```bash
# 1. Start your day
cd stir-craft/stircraft
git pull origin main                    # Get latest changes
./scripts/run_tests.sh                  # Verify everything works

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Development cycle
# Edit code...
./scripts/run_tests.sh                  # Run tests frequently
pipenv run python manage.py runserver  # Test in browser

# 4. Before committing
./scripts/run_tests.sh                  # Ensure all tests pass
git add .
git commit -m "feat: descriptive commit message"

# 5. Push and create PR
git push origin feature/your-feature-name
# Create Pull Request on GitHub
```

### **Commit Message Standards**

Use conventional commit format:
```
type(scope): description

feat(models): add cocktail ABV calculation
fix(views): resolve user authentication redirect
docs(readme): update setup instructions
test(forms): add validation test coverage
style(css): improve button contrast ratios
refactor(views): simplify list management logic
```

## 🧪 **Testing Guidelines**

### **Running Tests**

```bash
# Run all tests
./scripts/run_tests.sh

# Run with verbose output
./scripts/run_tests.sh --verbose

# Run specific test categories
pipenv run python manage.py test stir_craft.tests.test_models
pipenv run python manage.py test stir_craft.tests.test_views
pipenv run python manage.py test stir_craft.tests.test_forms
```

### **Writing Tests**

#### **Model Tests Example**
```python
from django.test import TestCase
from django.contrib.auth.models import User
from stir_craft.models import Cocktail, Ingredient

class CocktailModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        
    def test_cocktail_creation(self):
        cocktail = Cocktail.objects.create(
            name="Test Cocktail",
            instructions="Test instructions",
            creator=self.user
        )
        self.assertEqual(cocktail.name, "Test Cocktail")
        self.assertTrue(cocktail.is_alcoholic)  # Default value
```

#### **View Tests Example**
```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class CocktailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        
    def test_cocktail_list_view(self):
        response = self.client.get(reverse('cocktail_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cocktails')
```

### **Test Coverage Standards**
- **Models**: Test all methods, validations, and relationships
- **Views**: Test GET/POST requests, authentication, and permissions
- **Forms**: Test validation, error handling, and data processing
- **JavaScript**: Test user interactions and AJAX functionality

## 🎨 **Frontend Development**

### **CSS Organization**

```
stir_craft/static/css/
├── variables.css              # CSS custom properties (colors, spacing)
├── base.css                   # Base styles and typography
├── components.css             # Reusable UI components
├── contrast-overrides.css     # Accessibility and contrast fixes
└── pages/                     # Page-specific styles
```

#### **CSS Standards**
- **Use CSS Variables** - Consistent colors and spacing
- **Component-Based** - Reusable classes with clear names
- **Mobile-First** - Responsive design with min-width media queries
- **Accessibility** - WCAG AA compliance with high contrast

#### **CSS Naming Convention**
```css
/* Block Element Modifier (BEM) style */
.cocktail-card { }                 /* Block */
.cocktail-card__title { }          /* Element */
.cocktail-card--featured { }       /* Modifier */

/* Component classes */
.btn-primary { }                   /* Button component */
.form-group { }                    /* Form component */
.card-header { }                   /* Card component */
```

### **JavaScript Organization**

```
stir_craft/static/js/
├── components/                    # Reusable JavaScript components
│   ├── form-interactions.js       # Dynamic form behavior
│   ├── list-management.js         # List operation handlers
│   └── modal-handlers.js          # Modal interaction logic
└── tests/                         # JavaScript test files
    └── test-components.js         # Component test suite
```

#### **JavaScript Standards**
- **Modern ES6+** - Use const/let, arrow functions, and classes
- **Event Delegation** - Efficient event handling for dynamic content
- **Error Handling** - Proper try/catch blocks for AJAX calls
- **Testing** - Unit tests for all interactive components

## 🗄️ **Database Development**

### **Model Design Principles**

```python
class ExampleModel(models.Model):
    # 1. Required fields first
    name = models.CharField(max_length=100)
    
    # 2. Optional fields
    description = models.TextField(blank=True)
    
    # 3. Relationships
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 4. Metadata fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 5. Meta class
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Example Models"
    
    # 6. String representation
    def __str__(self):
        return self.name
    
    # 7. Custom methods
    def get_absolute_url(self):
        return reverse('example_detail', args=[self.pk])
```

### **Migration Best Practices**

```bash
# Create migrations for model changes
pipenv run python manage.py makemigrations

# Review generated migration before applying
cat stir_craft/migrations/0001_initial.py

# Apply migrations
pipenv run python manage.py migrate

# Check migration status
pipenv run python manage.py showmigrations
```

### **Database Queries**

Use efficient queries:
```python
# Good: Use select_related for foreign keys
cocktails = Cocktail.objects.select_related('creator', 'vessel').all()

# Good: Use prefetch_related for many-to-many
cocktails = Cocktail.objects.prefetch_related('ingredients', 'vibe_tags').all()

# Good: Filter at database level
popular_cocktails = Cocktail.objects.filter(
    in_lists__list_type='favorites'
).distinct()

# Avoid: N+1 queries
# for cocktail in cocktails:
#     print(cocktail.creator.username)  # Bad: generates query per cocktail
```

## 🔧 **Development Tools**

### **Available Scripts**

```bash
# Testing and quality assurance
./scripts/run_tests.sh                    # Run complete test suite
./scripts/run_tests.sh --verbose          # Detailed test output

# Database management
pipenv run python manage.py migrate           # Apply migrations
pipenv run python manage.py makemigrations    # Create new migrations
pipenv run python manage.py seed_dynamic_database  # Generate demo data

# Development server
pipenv run python manage.py runserver         # Start development server
pipenv run python manage.py collectstatic     # Collect static files
pipenv run python manage.py check             # Check for issues
```

### **Debugging Tools**

```python
# Use Django's built-in debugging
from django.conf import settings
if settings.DEBUG:
    import pdb; pdb.set_trace()  # Python debugger

# Use Django debug toolbar (install if needed)
pipenv install django-debug-toolbar

# Print SQL queries in development
from django.db import connection
print(connection.queries)
```

## 🔒 **Security Guidelines**

### **Always Validate Input**
```python
# In forms
class CocktailForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters.")
        return name

# In views
@require_POST
def add_to_list(request, cocktail_id, list_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
```

### **Protect Against Common Attacks**
- **CSRF**: Use `{% csrf_token %}` in all forms
- **XSS**: Use Django's template auto-escaping
- **SQL Injection**: Use Django ORM, never raw SQL with user input
- **Authentication**: Check `request.user.is_authenticated` for protected views

## 📋 **Code Review Checklist**

Before submitting a Pull Request:

### **Functionality**
- [ ] Feature works as intended
- [ ] Edge cases are handled
- [ ] Error messages are user-friendly
- [ ] Performance is acceptable

### **Code Quality**
- [ ] Code follows Django conventions
- [ ] Functions and classes have clear names
- [ ] Comments explain complex logic
- [ ] No duplicate code

### **Testing**
- [ ] All tests pass
- [ ] New features have tests
- [ ] Test coverage is adequate
- [ ] Tests use realistic data

### **Documentation**
- [ ] Code changes are documented
- [ ] API changes are documented
- [ ] Setup instructions are updated
- [ ] Comments explain non-obvious code

## 🚀 **Deployment Preparation**

### **Pre-deployment Checklist**
```bash
# Run full test suite
./scripts/run_tests.sh

# Check for migration issues
pipenv run python manage.py makemigrations --check

# Collect static files
pipenv run python manage.py collectstatic --noinput

# Verify settings
pipenv run python manage.py check --deploy
```

### **Environment Variables for Production**
```bash
DEBUG=False
SECRET_KEY=secure-production-key
DB_NAME=production_database
DB_HOST=production_host
ALLOWED_HOSTS=your-domain.com
```

## 📚 **Learning Resources**

### **Django Documentation**
- [Django Models](https://docs.djangoproject.com/en/4.2/topics/db/models/)
- [Django Views](https://docs.djangoproject.com/en/4.2/topics/http/views/)
- [Django Testing](https://docs.djangoproject.com/en/4.2/topics/testing/)

### **Best Practices**
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)
- [Python PEP 8](https://pep8.org/)

---

*This workflow guide is a living document. Update it as the project evolves and new practices are adopted.*

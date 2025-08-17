# Stir Craft – Internal Development Guide

Welcome to the main app## Development Guidelines

- Add new models, views, and templates inside `stir_craft/`.
- Use Django's app structure for scalability.
- Static files (images, CSS, JS) go in `stir_craft/static/`.
- Write tests in `stir_craft/tests.py`.
- Run tests before pushing:
  ```bash
  python manage.py test
  ```

## Data Management

### Using the Cocktail Import Command
The `seed_from_thecocktaildb` management command provides flexible options for importing cocktail data:

```bash
# Import a small test batch for development
python manage.py seed_from_thecocktaildb --limit 10

# Import from specific letters (useful for testing)
python manage.py seed_from_thecocktaildb --letters abc --limit 20

# Import a larger dataset for staging
python manage.py seed_from_thecocktaildb --limit 100

# Clear existing data and start fresh
python manage.py seed_from_thecocktaildb --clear --limit 25
```

### What the Import Does
- Fetches cocktail data from TheCocktailDB API
- Creates `Cocktail`, `Ingredient`, `Vessel`, and `RecipeComponent` records
- Intelligently categorizes ingredients (spirits, liqueurs, mixers, etc.)
- Parses measurements from text to structured data
- Adds flavor tags for filtering and search
- Provides comprehensive progress reporting

### Command Options
- `--limit N`: Import maximum N cocktails
- `--letters abc`: Only search letters a, b, c (useful for testing)
- `--clear`: Clear existing cocktail data before importing
- Default behavior: Import ALL available cocktails (500+)

## 🧩 Template Partials System (NEW!)

### Overview
We've implemented a template partials system to improve code reusability and maintainability. This works similar to React components, allowing us to break down complex templates into smaller, manageable pieces.

### What Are Template Partials?
Template partials are reusable template components that can be included in multiple templates using Django's `{% include %}` tag. They help reduce code duplication and make templates easier to read and maintain.

### Our Partials Structure
```
templates/stir_craft/partials/
├── _cocktail_header.html          # Cocktail name and edit buttons
├── _cocktail_meta.html            # Creator info, alcohol content, etc.
├── _ingredients_table.html        # Complete ingredients table
├── _user_lists_card.html         # User lists sidebar card
├── _ingredient_details_card.html  # Ingredient details sidebar
└── _quick_actions_card.html      # Quick actions sidebar
```

### Usage Guidelines

#### Including Partials
```django
<!-- Basic include -->
{% include 'stir_craft/partials/_cocktail_header.html' %}

<!-- Include with additional context -->
{% include 'stir_craft/partials/_ingredients_table.html' with components=recipe.components.all %}
```

#### Naming Conventions
- **File Names**: Use underscore prefix (e.g., `_component_name.html`)
- **Directory**: Store in `templates/app_name/partials/`
- **Purpose**: Name should clearly indicate what the partial contains

#### When to Create Partials
Create a partial when:
- A template section is used in multiple places
- A template becomes too long (>100 lines)
- A section has a clear, single responsibility
- You want to improve template readability

### Example: Refactoring a Large Template
**Before** (180 lines):
```django
<!-- cocktail_detail.html -->
<div class="card shadow">
    <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h1 class="mb-0">🍸 {{ cocktail.name }}</h1>
        <!-- ... 50 more lines of header code -->
    </div>
    <div class="card-body">
        <!-- ... 120 lines of body content -->
    </div>
</div>
```

**After** (40 lines):
```django
<!-- cocktail_detail.html -->
<div class="card shadow">
    {% include 'stir_craft/partials/_cocktail_header.html' %}
    <div class="card-body">
        {% include 'stir_craft/partials/_cocktail_meta.html' %}
        {% include 'stir_craft/partials/_ingredients_table.html' %}
        <!-- Instructions section stays inline as it's specific to this template -->
    </div>
</div>
```

### Best Practices

#### Context Management
- Partials inherit context from parent template
- Pass additional context using `with` keyword
- Keep partials focused on single responsibility

#### Testing Partials
- Test partials in isolation when possible
- Verify they work with different context data
- Check responsive behavior across devices

#### Documentation
- Comment the purpose of each partial
- Document required context variables
- Note any dependencies or assumptions

### Reusing Partials Across Templates

#### Cocktail Cards in Lists
```django
<!-- cocktail_list.html -->
{% for cocktail in cocktails %}
    <div class="col-md-4">
        <div class="card">
            {% include 'stir_craft/partials/_cocktail_header.html' %}
            <!-- Add specific list view content -->
        </div>
    </div>
{% endfor %}
```

#### Ingredient Information
```django
<!-- ingredient_detail.html -->
{% include 'stir_craft/partials/_ingredient_details_card.html' with components=ingredient.components.all %}
```

### Team Workflow for Partials

#### Creating New Partials
1. Identify reusable template sections
2. Extract to `partials/` directory with `_` prefix
3. Update original templates to use `{% include %}`
4. Test thoroughly across different contexts
5. Document the partial's purpose and context requirements

#### Modifying Existing Partials
1. Consider impact on all templates using the partial
2. Test changes across all usage contexts
3. Update documentation if context requirements change
4. Communicate changes to team

#### Code Review Focus
- Ensure partials have single responsibility
- Verify proper context management
- Check for responsive design
- Confirm accessibility standards

## 🍸 Cocktail Forms Development Guide

### Overview
The cocktail forms system provides a complete solution for creating and managing cocktail recipes with multiple ingredients, measurements, and preparation notes.

### Key Components

#### Forms (`forms/cocktail_forms.py`)
- **`CocktailForm`**: Main cocktail information (name, description, instructions, vessel, tags)
- **`RecipeComponentFormSet`**: Manages multiple ingredients using Django's inline formsets
- **`CocktailSearchForm`**: Advanced search and filtering capabilities
- **`QuickIngredientForm`**: For future modal ingredient creation

#### Views Added
- **`cocktail_create`**: Handle formset creation with proper validation
- **`cocktail_list`**: Browse cocktails with search/filter/pagination
- **`cocktail_detail`**: Display complete recipe with stats and actions

#### Templates Created
- **`cocktail_create.html`**: Dynamic form with ingredient management
- **`cocktail_list.html`**: Responsive cocktail browsing interface
- **`cocktail_detail.html`**: Complete recipe display with nutritional info

### Development Guidelines for Forms

#### Creating New Forms
```python
# Example: Creating a custom form
class MyCustomForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = ['field1', 'field2']
        widgets = {
            'field1': forms.TextInput(attrs={'class': 'form-control'}),
        }
```

#### Working with Formsets
```python
# Using inline formsets for related models
MyFormSet = inlineformset_factory(
    parent_model=ParentModel,
    model=ChildModel,
    fields=['field1', 'field2'],
    extra=3,  # Number of empty forms
    min_num=1,  # Minimum required forms
    max_num=10,  # Maximum allowed forms
    can_delete=True
)
```

#### Template Integration
```django
<!-- Form rendering with Bootstrap styling -->
<div class="mb-3">
    <label for="{{ form.field.id_for_label }}" class="form-label">{{ form.field.label }}</label>
    {{ form.field }}
    {% if form.field.errors %}
        <div class="invalid-feedback d-block">{{ form.field.errors.0 }}</div>
    {% endif %}
</div>
```

### Testing Forms
```python
# Example form test
def test_cocktail_form_valid(self):
    form_data = {
        'name': 'Test Cocktail',
        'instructions': 'Mix well',
        'is_alcoholic': True
    }
    form = CocktailForm(data=form_data)
    self.assertTrue(form.is_valid())
```

### URL Patterns
Add these to your URL configuration:
```python
urlpatterns = [
    path('cocktails/', views.cocktail_list, name='cocktail_list'),
    path('cocktails/create/', views.cocktail_create, name='cocktail_create'),
    path('cocktails/<int:cocktail_id>/', views.cocktail_detail, name='cocktail_detail'),
]
```r Stir Craft! This document outlines the steps and best practices for developing our cocktail and mocktail app.

## 🚀 Recent Updates

### Cocktail Forms & Views System (NEW!)
- **Advanced Form Implementation**: Complete cocktail creation system using Django inline formsets
- **Dynamic Ingredient Management**: Add/remove ingredients with real-time validation
- **Professional Templates**: Bootstrap-styled responsive forms with JavaScript enhancements
- **Comprehensive Views**: Create, browse, detail, and search functionality
- **Search & Filter**: Advanced cocktail discovery with multi-field filtering

### API Integration & Database Seeding
- **TheCocktailDB API Integration**: Added comprehensive data seeding from a reliable cocktail API
- **PostgreSQL Configuration**: Database configured with proper authentication and optimization
- **Management Commands**: Custom Django commands for data import and maintenance
- **Intelligent Data Processing**: Automated categorization and parsing of cocktail data

### Management Commands
- `seed_from_thecocktaildb`: Import cocktail data with intelligent processing
- Comprehensive error handling and progress reporting
- Flexible options for testing and production use

## Project Structure

- All main app code should be placed in the `stir_craft/` directory (this folder).
- Avoid placing new code in higher-level directories unless absolutely necessary.

## Workflow & Branching

- **Always commit changes to your personal branch** (the one with your name on it). Do **not** commit directly to `main`.
- Open a pull request when your feature or fix is ready for review and merging.

## Current Focus: Wireframes

- We are currently working on wireframes to visualize the project pages.
- Wireframes and design assets are in `static/images/wireframes/`.
- Once wireframes are complete, we will move on to building out the models.

## Setup

1. **Clone the repository** and create/switch to your personal branch.
2. **Install dependencies**:
   ```bash
   pipenv install
   ```
3. **Activate the virtual environment**:
   ```bash
   pipenv shell
   ```
4. **Ensure PostgreSQL is running** and database is configured (see main README.md).
5. **Navigate to the Django project**:
   ```bash
   cd stircraft
   ```
6. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```
7. **Seed the database with cocktail data**:
   ```bash
   python manage.py seed_from_thecocktaildb --limit 10
   ```
8. **Create a superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```
9. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

## Development Guidelines

- Add new models, views, and templates inside `stir_craft/`.
- Use Django’s app structure for scalability.
- Static files (images, CSS, JS) go in `stir_craft/static/`.
- Write tests in `stir_craft/tests.py`.
- Run tests before pushing:
  ```bash
  python manage.py test
  ```

## Testing Framework

We have implemented a comprehensive testing scaffold to ensure the reliability of our models and features. Follow these steps to use the testing framework after creating a new feature:

1. **Write Tests for Your Feature:**
   - Add test methods to the appropriate test class in `stir_craft/tests.py`.
   - Use assertions to validate expected behavior (e.g., `assertEqual`, `assertTrue`).
   - If your feature involves multiple models, write integration tests to verify their interactions.

2. **Run Tests Locally:**
   ```bash
   python manage.py test stir_craft
   ```
   - Use `--verbosity=2` for detailed output.
   - Target specific test classes or methods if needed.

3. **Fix Any Failures:**
   - Debug and resolve issues until all tests pass.

4. **Push Your Changes:**
   - Ensure your branch is up to date with `main`.
   - Commit and push your changes to the Feature Branch, including the updated tests.
   - Include your tests in the pull request to Testing Branch.

By maintaining high test coverage, we can ensure the stability and scalability of the Stir Craft app.

## Code Review & Merging

- Open a pull request for review.
- Ensure all tests pass and code follows team conventions.
- Only merge after approval.

## Keeping Your Local Repo Up to Date

To make sure your local repository stays current with the latest changes from the remote (cloud) repository:

1. **Fetch and merge the latest changes from main:**
   ```bash
   git checkout main
   git pull origin main
   ```
2. **Switch back to your personal branch and rebase (or merge) main into it:**
   ```bash
   git checkout <your-branch-name>
   git rebase main
   # or, if you prefer merging:
   git merge main
   ```
3. **Resolve any conflicts, test your code, and continue working.**

Keeping your branch up to date helps avoid merge conflicts and ensures you’re working with the latest code.

## Branch Update Utility

To ensure your local repository stays up to date and avoid merge conflicts, use the `update_branches_team.sh` script before committing changes:

1. **Run the script:**
   ```bash
   ./update_branches_team.sh
   ```
   - This script will fetch the latest changes from the remote repository and update all local branches.
   - Replace `/path/to/your/local/stir-craft` in the script with your local repository path if needed.

2. **Verify updates:**
   - Ensure your branch is up to date with `main`.
   - Resolve any conflicts if they arise.

3. **Switch back to your feature branch:**
   - The script ends with your repository on the `main` branch.
   - Use the following command to return to your feature branch:
     ```bash
     git checkout <your-branch-name>
     ```

By running this utility regularly, you can maintain consistency across team workflows and minimize conflicts during development.

## Additional Notes

- Refer to the main project README for deployment and environment details.
- Keep this document updated as the project evolves.
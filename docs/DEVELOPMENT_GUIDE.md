# Stir Craft – Development Guide

**Prerequisites:** Make sure you've completed the setup in `docs/QUICK_SETUP.md` and `docs/POSTGRES_SETUP.md` first.

## 🛠 Available Scripts

**Essential scripts for daily development:**

```bash
./scripts/run_tests.sh              # Run all tests (do this often!)
./scripts/run_tests.sh --verbose    # Detailed test output for debugging
./scripts/update_branches_team.sh   # Sync your local branches with team changes  
./scripts/update_test_report.py     # Auto-generate test failure reports
```

## Development Guidelines

- Add new models, views, and templates inside `stir_craft/`.
- Use Django's app structure for scalability.
- Static files (images, CSS, JS) go in `stir_craft/static/`.
- Write tests in `stir_craft/tests/` (modular test files under `stir_craft/tests/`).
- Run tests before pushing:
  ```bash
  ./scripts/run_tests.sh
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

## 🎨 CSS Organization & Styling (NEW!)

### CSS Architecture Overview
We've implemented a professional CSS organization system that separates global styles from page-specific styles for better maintainability and scalability.

### CSS File Structure
```
stircraft/stir_craft/static/css/
├── base.css          # Global styles and reusable components
└── dashboard.css     # Dashboard-specific styles
```

### CSS Organization Guidelines

#### Global Styles (base.css)
- **Component styles**: Reusable UI components used across multiple templates
- **Utility classes**: Common styling patterns and helpers
- **Typography**: Global font settings and text styling
- **Layout helpers**: Flexbox utilities, spacing, and grid helpers
- **Form styling**: Consistent form element appearance

#### Page-Specific Styles (dashboard.css)
- **Page layout**: Styles specific to the dashboard page
- **Custom components**: Dashboard-only components
- **Responsive adjustments**: Page-specific responsive behavior
- **Interactive elements**: Dashboard-specific hover and focus states

### CSS Naming Conventions
We follow a semantic naming approach:
```css
/* Component-based naming */
.profile-header { }
.list-card { }
.cocktail-grid { }

/* State-based naming */
.is-editable { }
.is-loading { }
.has-content { }

/* Modifier naming */
.list-card--favorites { }
.cocktail-card--featured { }
```

### Adding New Styles

#### For Global Components
Add to `base.css` when:
- The style will be used across multiple templates
- It's a reusable UI component
- It's a utility class or helper

#### For Page-Specific Styles
Add to page-specific CSS files when:
- The style is unique to one page/template
- It modifies existing components for specific contexts
- It handles page-specific responsive behavior

### CSS Best Practices
- **No inline styles**: All styles must be in CSS files
- **Semantic class names**: Use descriptive, meaningful class names
- **Component thinking**: Group related styles together
- **Responsive design**: Mobile-first approach with progressive enhancement
- **Performance**: Use efficient selectors and minimal nesting

### Template Integration
```django
<!-- In base.html -->
<link rel="stylesheet" href="{% static 'css/base.css' %}">

<!-- In specific templates -->
<link rel="stylesheet" href="{% static 'css/dashboard.css' %}">
```

For detailed CSS guidelines, see **[CSS_ORGANIZATION.md](../docs/CSS_ORGANIZATION.md)**.

## 🧩 Template Partials System (NEW!)

### Overview
We've implemented a template partials system to improve code reusability and maintainability. This works similar to React components, allowing us to break down complex templates into smaller, manageable pieces.

### What Are Template Partials?
Template partials are reusable template components that can be included in multiple templates using Django's `{% include %}` tag. They help reduce code duplication and make templates easier to read and maintain.

### Our Partials Structure
```
templates/stir_craft/partials/
├── _profile_header.html           # User profile display
├── _profile_stats.html            # Cocktail statistics  
├── _profile_actions.html          # Profile action buttons
├── _favorites_section.html        # Favorites list display
├── _creations_section.html        # User creations display
├── _lists_section.html            # Custom lists management
├── _list_card.html               # Individual list component
├── _list_actions.html            # List action buttons
├── _cocktail_grid.html           # Cocktail display grid
├── _cocktail_card.html           # Individual cocktail card
├── _empty_state.html             # Empty list placeholder
└── _loading_spinner.html         # Loading state component
```

### Usage Guidelines

#### Including Partials
```django
<!-- Basic include -->
{% include 'stir_craft/partials/_profile_header.html' %}

<!-- Include with additional context -->
{% include 'stir_craft/partials/_cocktail_grid.html' with cocktails=user_cocktails %}
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

### Example: Dashboard Implementation
The dashboard template uses partials extensively:
```django
<!-- dashboard.html (clean and readable) -->
<div class="dashboard-container">
    <div class="row">
        <div class="col-lg-8">
            {% include 'stir_craft/partials/_profile_header.html' %}
            {% include 'stir_craft/partials/_favorites_section.html' %}
            {% include 'stir_craft/partials/_creations_section.html' %}
        </div>
        <div class="col-lg-4">
            {% include 'stir_craft/partials/_profile_stats.html' %}
            {% include 'stir_craft/partials/_lists_section.html' %}
        </div>
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
<!-- cocktail_index.html -->
{% for cocktail in cocktails %}
    <div class="col-md-4">
        {% include 'stir_craft/partials/_cocktail_card.html' %}
    </div>
{% endfor %}
```

#### Profile Information
```django
<!-- user_profile.html -->
{% include 'stir_craft/partials/_profile_header.html' %}
{% include 'stir_craft/partials/_profile_stats.html' %}
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

For detailed template partials guidance, see **[TEMPLATE_PARTIALS_GUIDE.md](../docs/TEMPLATE_PARTIALS_GUIDE.md)**.

## 🚀 Recent Updates

### Dashboard Implementation System (NEW!)
- **Auto-Managed Lists**: "Your Creations" lists that automatically sync with user's cocktails
- **Enhanced List Model**: Added list_type, is_editable, is_deletable fields with Django signals
- **Template Partials**: 12 reusable components for better maintainability and code organization
- **CSS Organization**: Professional styling system with separated global and page-specific styles

### Cocktail Forms & Views System
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

### 1. Clone Repository & Install Dependencies
```bash
# Clone the repository and switch to your personal branch
git clone <repository-url>
cd stir-craft
git checkout <your-branch-name>

# Install Python dependencies
pipenv install
```

### 2. PostgreSQL Database Setup

This project requires PostgreSQL. Follow these steps to set up your local database:

#### Install PostgreSQL (if not already installed)
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install postgresql postgresql-contrib

# macOS with Homebrew
brew install postgresql
brew services start postgresql

# Check if PostgreSQL is running
sudo systemctl status postgresql    # Linux
brew services list | grep postgres  # macOS
```

#### Create Database User and Database
```bash
# Create a PostgreSQL user for the project
sudo -u postgres createuser --interactive --pwprompt macfarley
# When prompted, enter password: stircraft123
# Answer 'n' to superuser, 'y' to create databases, 'n' to create roles

# Create the project database
sudo -u postgres createdb --owner=macfarley stircraft

# Alternative: Use psql directly
sudo -u postgres psql
CREATE USER macfarley WITH PASSWORD 'stircraft123';
CREATE DATABASE stircraft OWNER macfarley;
GRANT ALL PRIVILEGES ON DATABASE stircraft TO macfarley;
\q
```

#### Configure Environment Variables
The Django settings use environment variables for database configuration:

```bash
# Add to your ~/.bashrc, ~/.zshrc, or create a .env file:
export DB_PASSWORD="stircraft123"

# Optional: Override other database settings if needed
export DB_NAME="stircraft"
export DB_USER="macfarley" 
export DB_HOST="localhost"
export DB_PORT="5432"

# Reload your shell or source the file
source ~/.bashrc  # or ~/.zshrc
```

### 3. Django Setup & Migrations

```bash
# Activate the virtual environment
pipenv shell

# Navigate to Django project directory
cd stircraft

# Set database password for this session
export DB_PASSWORD="stircraft123"

# Run Django system check
python manage.py check

# Apply database migrations
python manage.py migrate

# Create a superuser account (optional but recommended)
python manage.py createsuperuser

# Seed the database with cocktail data
python manage.py seed_from_thecocktaildb --limit 10

# Start the development server
python manage.py runserver
```

### 4. Verify Setup

Test that everything is working:

```bash
# Run system checks
export DB_PASSWORD="stircraft123"
pipenv run python stircraft/manage.py check

# Test database connection
pipenv run python stircraft/manage.py shell -c "from django.contrib.auth.models import User; print(f'Users: {User.objects.count()}')"

# Run the development server
pipenv run python stircraft/manage.py runserver
```

### Troubleshooting Database Issues

#### Connection Refused
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list               # macOS

# Start PostgreSQL if not running
sudo systemctl start postgresql  # Linux  
brew services start postgresql   # macOS
```

#### Authentication Failed
```bash
# Reset user password
sudo -u postgres psql -c "ALTER USER macfarley PASSWORD 'stircraft123';"

# Ensure database exists and is owned by user
sudo -u postgres psql -c "\l"  # List databases
sudo -u postgres psql -c "ALTER DATABASE stircraft OWNER TO macfarley;"
```

#### Environment Variables Not Set
```bash
# Temporarily set for current session
export DB_PASSWORD="stircraft123"

# Permanently add to shell profile
echo 'export DB_PASSWORD="stircraft123"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc
```

### Quick Reference for Team Members

**Essential Commands (run these every time):**
```bash
# Set database password
export DB_PASSWORD="stircraft123"

# Common Django commands
pipenv run python stircraft/manage.py migrate
pipenv run python stircraft/manage.py runserver
pipenv run python stircraft/manage.py shell
pipenv run python stircraft/manage.py createsuperuser

# Import cocktail data
pipenv run python stircraft/manage.py seed_from_thecocktaildb --limit 10
```

**First-time setup checklist:**
- [ ] PostgreSQL installed and running
- [ ] Database `stircraft` created with user `macfarley`
- [ ] Environment variable `DB_PASSWORD="stircraft123"` set
- [ ] Dependencies installed with `pipenv install`
- [ ] Migrations applied with `python manage.py migrate`
- [ ] Superuser created (optional)
- [ ] Test data imported (optional)

---

## Development Guidelines

- Add new models, views, and templates inside `stir_craft/`.
- Use Django’s app structure for scalability.
- Static files (images, CSS, JS) go in `stir_craft/static/`.
- Write tests in `stir_craft/tests/` (modular test files under `stir_craft/tests/`).
- Run tests before pushing:
  ```bash
  python manage.py test
  ```

## Testing Framework

We have implemented a comprehensive testing scaffold to ensure the reliability of our models and features. Follow these steps to use the testing framework after creating a new feature:

1. **Write Tests for Your Feature:**
   - Add test methods to the appropriate test file under `stir_craft/tests/`.
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
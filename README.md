# StirCraft: Cocktail Recipe Manager

## 🥂 Overview
**StirCraft** is a cocktail recipe manager and builder designed for flavor-forward exploration. Users can browse, create, and organize recipes, ingredients, and vessels — with dynamic filtering by vibe, flavor profile, and color. The app emphasizes modularity, user ownership, and playful branding.

---

## 🚀 Current Implementation

### ✅ API Integration & Data Seeding
- **TheCocktailDB API Integration**: Custom Django management command to seed database with real cocktail data
- **PostgreSQL Database**: Configured with user authentication and optimized for cocktail recipe storage
- **Intelligent Data Processing**: Automated ingredient categorization, measurement parsing, and vessel matching
- **Management Commands**: `seed_from_thecocktaildb` command for importing cocktail data with comprehensive error handling

### ✅ Cocktail Forms & Views
- **Advanced Form System**: Complete cocktail creation with inline formsets for multiple ingredients
- **Dynamic Ingredient Management**: Add/remove ingredients with proper Django formset validation
- **Pure Django Solution**: No JavaScript required - leverages Django's built-in formset capabilities
- **Comprehensive Views**: Create, list, detail, and search functionality for cocktails
- **Professional Templates**: Bootstrap-styled forms with proper error handling and user feedback
- **Template Partials**: Modular, reusable template components for improved maintainability
- **Search & Filter**: Advanced cocktail filtering by ingredients, vessel type, alcohol content, and more

### ✅ Wireframes Completed
- **Auth Page**: Combined Sign Up / Sign In with toggle (mobile) or side-by-side forms (desktop)
- **Dashboard View**: Profile info, user-created lists, and recipes with "Add New" buttons
- **Master Ingredients List**: Filterable by flavor tags (using `TaggableManager`), with responsive ingredient cards
- **Error Page Template**: Displays error message, hero logo, and link to home
- **Vessel Management Page**: Unified list and creation form; form is modular for reuse in recipe creation
- **Recipe Catalog Page**: Filterable list with vibe, flavor, and color selectors; popularity counter ("On X Lists"); single "Add New Recipe" button

### ✅ Models & Testing
- **Ingredient model** uses `django-taggit` for flavor tags
- **Model tests scaffolded** for Ingredient, Recipe, and List
- Sample test for `Ingredient.flavor_tags` using `TaggableManager`
- Plan to modularize form logic for reuse across views

### ✅ Git Workflow
- Shell script created to update all local branches from remote (`origin`)
- Testing strategy outlined using Django's `TestCase`, `setUpTestData`, and assertions

---

## 🎨 Frontend Styling: Bootstrap

This project uses [Bootstrap](https://getbootstrap.com/) for frontend styling. Bootstrap provides CSS classes (e.g., `card-header`, `btn`, etc.) used throughout our templates.

### How to Enable Bootstrap

**Recommended (CDN):**
Add the following line to the `<head>` section of your `base.html` template:

```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
```

This loads Bootstrap from the web. No installation is required.

**Optional (Local Install):**
If you prefer to use a local copy, you can download Bootstrap or install it via npm:

```sh
npm install bootstrap
```

Then link to the CSS file in your static files setup. See the [Bootstrap docs](https://getbootstrap.com/docs/5.3/getting-started/download/) for details.

### Why Bootstrap?
Bootstrap makes it easy to create responsive, modern layouts and UI components. All team members should ensure Bootstrap is enabled to see the intended styles.

---

## 🎯 MVP Goals

### Core Features
- User authentication (Sign Up / Sign In)
- Dashboard with editable profile, user-created lists, and recipes
- Ingredient and vessel management with reusable forms
- Recipe creation with dynamic ingredient and vessel selection
- Recipe catalog with filtering by vibe, flavor tags, and color
- Error handling views for bad paths, restricted access, and failed requests

### Technical Stack
- **Backend**: Django 5.2.5 + PostgreSQL
- **API Integration**: TheCocktailDB API for real cocktail data
- **Data Processing**: Intelligent ingredient categorization and measurement parsing
- **Frontend**: Django templates with Bootstrap CSS
- **Tagging**: `django-taggit` for flavor profiles
- **Testing**: Django's built-in test framework
- **Version Control**: Git + GitHub

### ✅ Wireframes Completed

### ✅ Models & Testing
- **Ingredient model** uses `django-taggit` for flavor tags
- **Model tests scaffolded** for Ingredient, Recipe, and List
- Sample test for `Ingredient.flavor_tags` using `TaggableManager`
- Plan to modularize form logic for reuse across views

### ✅ Cocktail Forms & Views (NEW!)
- **Advanced Form System**: Complete cocktail creation with inline formsets for multiple ingredients
- **Dynamic Ingredient Management**: Add/remove ingredients with proper Django formset validation
- **Pure Django Solution**: No JavaScript required - leverages Django's built-in formset capabilities
- **Comprehensive Views**: Create, list, detail, and search functionality for cocktails
- **Professional Templates**: Bootstrap-styled forms with proper error handling and user feedback
- **Search & Filter**: Advanced cocktail filtering by ingredients, vessel type, alcohol content, and more

### ✅ Git Workflow
- Shell script created to update all local branches from remote (`origin`)
- Testing strategy outlined using Django’s `TestCase`, `setUpTestData`, and assertions

---

## 🎯 MVP Goals

### Core Features
- User authentication (Sign Up / Sign In)
- Dashboard with editable profile, user-created lists, and recipes
- Ingredient and vessel management with reusable forms
- Recipe creation with dynamic ingredient and vessel selection
- Recipe catalog with filtering by vibe, flavor tags, and color
- Error handling views for bad paths, restricted access, and failed requests

### Technical Stack
- **Backend**: Django + Postgres
- **Frontend**: Django templates with vanilla CSS
- **Tagging**: `django-taggit` for flavor profiles
- **Testing**: Django’s built-in test framework
- **Version Control**: Git + GitHub

---

## ✨ Stretch Goals

### UX & Features
- Social login (Google, GitHub)
- Recipe remixing and forking
- Ingredient detail pages with usage stats
- Color picker or auto-detection for cocktail color
- Vibe-based sorting (e.g., “Cozy,” “Tropical,” “Party”)
- User badges or achievements (e.g., “Citrus Connoisseur”)

### Technical Enhancements
- API endpoints for recipes, ingredients, and lists
- Responsive design with mobile-first layout
- Inline form validation and error messaging
- Admin dashboard for moderation or featured recipes
- CI/CD pipeline with test coverage tracking

---

## 🍸 Cocktail Forms System (NEW!)

### Overview
StirCraft now includes a comprehensive cocktail creation and management system using Django's inline formsets. This allows users to create complex cocktail recipes with multiple ingredients, measurements, and preparation notes in a single, intuitive form.

### Key Components

#### **Forms (`cocktail_forms.py`)**
- **`CocktailForm`**: Main cocktail information (name, description, instructions, vessel, tags)
- **`RecipeComponentForm`**: Individual ingredient with amount, unit, and preparation notes
- **`RecipeComponentFormSet`**: Manages multiple ingredients using Django's `inlineformset_factory`
- **`QuickIngredientForm`**: For adding new ingredients on-the-fly (future modal integration)
- **`CocktailSearchForm`**: Advanced search and filtering for cocktail browsing

#### **Views**
- **`cocktail_create`**: Handles formset creation with proper validation and error handling
- **`cocktail_index`**: Browse cocktails with search, filter, and pagination
- **`cocktail_detail`**: Full recipe display with stats, ingredient details, and user actions

#### **Templates**
- **`cocktail_create.html`**: Rich form interface with dynamic ingredient management
- **`cocktail_index.html`**: Responsive cocktail browsing with search filters
- **`cocktail_detail.html`**: Complete recipe display with nutritional info and actions

### Features

#### **Dynamic Form Management**
- Django formset handles multiple ingredients seamlessly
- Automatic form validation for required fields
- Smart alcohol content calculation based on ingredients
- Order management for ingredient addition sequence

#### **Advanced Validation**
- Minimum 1 ingredient required per cocktail
- Maximum 15 ingredients to prevent abuse
- Proper unit validation with predefined choices
- Age verification integration for alcoholic beverages

#### **User Experience**
- Bootstrap-styled responsive forms
- Clear error messaging and field validation
- Helpful tips and user guidance
- Mobile-optimized form layouts

#### **Search & Filter Capabilities**
- Text search across cocktail names and descriptions
- Filter by specific ingredients or vessel types
- Alcoholic/non-alcoholic filtering
- Color-based filtering
- Sort by creation date, name, or creator

### Usage Examples

#### **Creating a Cocktail**
```python
# In views.py - the formset handles both cocktail and ingredients
cocktail_form = CocktailForm(user=request.user)
formset = RecipeComponentFormSet()

# Form validates both main cocktail and all ingredients
if cocktail_form.is_valid() and formset.is_valid():
    cocktail = cocktail_form.save(commit=False)
    cocktail.creator = request.user
    cocktail.save()
    
    formset.instance = cocktail
    components = formset.save()
```

#### **Template Integration**
```django
<!-- cocktail_create.html -->
{{ formset.management_form }}
{% for form in formset %}
    <div class="ingredient-row">
        {{ form.ingredient }}
        {{ form.amount }} {{ form.unit }}
        {{ form.preparation_note }}
    </div>
{% endfor %}
```

### URLs Added
- `/cocktails/` - Browse all cocktails
- `/cocktails/create/` - Create new cocktail
- `/cocktails/<id>/` - View cocktail details

### Technical Implementation Notes

#### **Why Inline Formsets?**
1. **Perfect Model Match**: Your `RecipeComponent` join table is designed exactly for this pattern
2. **Clean Data Structure**: Each ingredient has precise amount, unit, and preparation notes
3. **Django-Native**: Uses built-in `inlineformset_factory` - no custom JavaScript required initially
4. **Scalable**: Easy to enhance with AJAX and dynamic features later

#### **Performance Optimizations**
- Uses `select_related()` and `prefetch_related()` for efficient queries
- Pagination for large cocktail lists
- Indexed database fields for fast searching
- Minimal template queries with optimized context

### Future Enhancements
1. **AJAX Integration**: Add ingredients without page refresh
2. **Auto-suggestions**: Typeahead for ingredient selection
3. **Recipe Import**: Bulk import from cocktail APIs
4. **Image Uploads**: Add cocktail photos
5. **Advanced Validation**: Ingredient compatibility checking

---
- StirCraft evokes creativity, modularity, and flavor exploration
- Wireframes and UI lean into playful but clean design
- Flavor tags and vibe filters support expressive, user-driven discovery

---

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.12+
- PostgreSQL
- Git

### Database Setup
1. **Install and start PostgreSQL:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql
   
   # macOS with Homebrew
   brew install postgresql
   brew services start postgresql
   ```

2. **Create database and user:**
   ```bash
   sudo -u postgres createuser --interactive --pwprompt macfarley
   # Enter password: stircraft123 when prompted
   
   sudo -u postgres createdb --owner=macfarley stircraft
   ```

3. **Set environment variables:**
   ```bash
   # Add to your shell profile (~/.bashrc or ~/.zshrc)
   export DB_PASSWORD="stircraft123"
   
   # Or set for current session only
   export DB_PASSWORD="stircraft123"
   ```

   **Note**: The application uses environment variables for database configuration. See `docs/DEVELOPMENT_GUIDE.md` for detailed setup instructions and troubleshooting.

### Application Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/General-Assembly-Team-1/stir-craft.git
   ```

2. **Navigate to the project directory:**
   ```bash
   cd stir-craft
   ```

3. **Install dependencies:**
   ```bash
   pipenv install
   ```

4. **Activate the virtual environment:**
   ```bash
   pipenv shell
   ```

5. **Navigate to the Django project:**
   ```bash
   cd stircraft
   ```

6. **Set database password and apply migrations:**
   ```bash
   # Set the database password for this session
   export DB_PASSWORD="stircraft123"
   
   # Apply database migrations
   python manage.py migrate
   ```

7. **Seed the database with cocktail data:**
   ```bash
   # Import a small test batch (10 cocktails)  
   python manage.py seed_from_thecocktaildb --limit 10
   
   # Import 100 cocktails from all letters
   python manage.py seed_from_thecocktaildb --limit 100
   
   # Import ALL available cocktails (could be 500+)
   python manage.py seed_from_thecocktaildb
   ```

8. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

9. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

10. **Access the application:**
    - Main application: http://127.0.0.1:8000/
    - Admin interface: http://127.0.0.1:8000/admin/

---

## 📊 Data Management

### Cocktail Data Seeding
The project includes a comprehensive management command to populate the database with real cocktail data from TheCocktailDB API:

```bash
# Basic usage - import 10 cocktails for testing
python manage.py seed_from_thecocktaildb --limit 10

# Import specific number of cocktails
python manage.py seed_from_thecocktaildb --limit 50

# Import from specific letters only
python manage.py seed_from_thecocktaildb --letters abc --limit 20

# Import ALL available cocktails (500+)
python manage.py seed_from_thecocktaildb

# Clear existing data and start fresh
python manage.py seed_from_thecocktaildb --clear --limit 25
```

### What Gets Imported
- **Cocktails**: Name, instructions, image URLs, categories
- **Ingredients**: Automatically categorized (spirits, liqueurs, mixers, etc.) with alcohol content estimation
- **Vessels**: Glassware types matched to StirCraft's vessel system
- **Recipe Components**: Measurements parsed from text to structured data
- **Flavor Tags**: Intelligent tagging for advanced filtering

### Data Processing Features
- **Smart Categorization**: Ingredients are automatically categorized as spirits, liqueurs, mixers, etc.
- **Measurement Parsing**: Text measurements like "1 oz" or "2 dashes" are converted to structured data
- **Alcohol Content**: Estimated alcohol percentages for ingredients
- **Duplicate Prevention**: Uses `get_or_create()` to avoid duplicate entries
- **Error Handling**: Robust error recovery and detailed logging

---

## 🧪 Testing

1. **Run all tests:**
   ```bash
   python manage.py test
   ```

2. **Run specific app tests:**
   ```bash
   python manage.py test stir_craft
   ```

3. **Run with verbose output:**
   ```bash
   python manage.py test --verbosity=2
   ```

---

## 🧠 Contribution Guidelines

1. **Create a personal branch:**
   ```bash
   git checkout -b <your-branch-name>
   ```

2. **Commit changes to your branch:**
   ```bash
   git add .
   git commit -m "Your commit message"
   ```

3. **Push your branch:**
   ```bash
   git push origin <your-branch-name>
   ```

4. **Open a pull request for review.**

---

## 📚 Documentation

For detailed technical documentation, development guides, and project history, see the **[docs/](./docs/)** folder:

- **[Development Guide](./docs/DEVELOPMENT_GUIDE.md)** - Setup, workflow, and contribution guidelines
- **[Cocktail Forms Technical Guide](./docs/COCKTAIL_FORMS_TECHNICAL_GUIDE.md)** - Complete technical documentation for the forms system
- **[Project Changelog](./docs/PROJECT_CHANGELOG.md)** - Detailed development history and milestones

---

*For questions or support, please refer to the documentation or contact the development team.*

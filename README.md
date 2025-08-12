# StirCraft: Cocktail Recipe Manager

## 🥂 O### Technical Stack
- **Backend**: Django 5.2.5 + PostgreSQL
- **API Integration**: TheCocktailDB API for real cocktail data
- **Data Processing**: Intelligent ingredient categorization and measurement parsing
- **Frontend**: Django templates with vanilla CSS
- **Tagging**: `django-taggit` for flavor profiles
- **Testing**: Django's built-in test framework
- **Version Control**: Git + GitHubw
**StirCraft** is a cocktail recipe manager and builder designed for flavor-forward exploration. Users can browse, create, and organize recipes, ingredients, and vessels — with dynamic filtering by vibe, flavor profile, and color. The app emphasizes modularity, user ownership, and playful branding.

---

## 🚀 Current Implementation

### ✅ API Integration & Data Seeding
- **TheCocktailDB API Integration**: Custom Django management command to seed database with real cocktail data
- **PostgreSQL Database**: Configured with user authentication and optimized for cocktail recipe storage
- **Intelligent Data Processing**: Automated ingredient categorization, measurement parsing, and vessel matching
- **Management Commands**: `seed_from_thecocktaildb` command for importing cocktail data with comprehensive error handling

### ✅ Wireframes Completed
- **Auth Page**: Combined Sign Up / Sign In with toggle (mobile) or side-by-side forms (desktop)
- **Dashboard View**: Profile info, user-created lists, and recipes with “Add New” buttons
- **Master Ingredients List**: Filterable by flavor tags (using `TaggableManager`), with responsive ingredient cards
- **Error Page Template**: Displays error message, hero logo, and link to home
- **Vessel Management Page**: Unified list and creation form; form is modular for reuse in recipe creation
- **Recipe Catalog Page**: Filterable list with vibe, flavor, and color selectors; popularity counter (“On X Lists”); single “Add New Recipe” button

### ✅ Models & Testing
- **Ingredient model** uses `django-taggit` for flavor tags
- **Model tests scaffolded** for Ingredient, Recipe, and List
- Sample test for `Ingredient.flavor_tags` using `TaggableManager`
- Plan to modularize form logic for reuse across views

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

## 🧠 Naming & Branding Notes
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
   sudo -u postgres psql
   CREATE DATABASE stircraft;
   CREATE USER macfarley WITH PASSWORD 'stircraft123';
   GRANT ALL PRIVILEGES ON DATABASE stircraft TO macfarley;
   \q
   ```

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

6. **Apply migrations:**
   ```bash
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

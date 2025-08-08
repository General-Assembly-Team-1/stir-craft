# StirCraft: Cocktail Recipe Manager

## 🥂 Overview
**StirCraft** is a cocktail recipe manager and builder designed for flavor-forward exploration. Users can browse, create, and organize recipes, ingredients, and vessels — with dynamic filtering by vibe, flavor profile, and color. The app emphasizes modularity, user ownership, and playful branding.

---

## 🚀 Current Implementation

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

5. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

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
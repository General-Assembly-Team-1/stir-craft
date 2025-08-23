# 🍸 StirCraft: Cocktail Recipe Manager

![StirCraft Logo](https://via.placeholder.com/800x400/2c3e50/ecf0f1?text=StirCraft+🍹+Cocktail+Recipe+Manager)

## About StirCraft

**StirCraft** is a comprehensive cocktail recipe management application that empowers mixology enthusiasts to discover, create, and organize their favorite cocktail recipes. Whether you're a professional bartender or a home cocktail enthusiast, StirCraft provides the tools you need to build your personal cocktail library.

### Why We Built StirCraft

As cocktail enthusiasts ourselves, we recognized the need for a centralized platform where users could:
- Discover new cocktail recipes from a vast database
- Create and customize their own unique recipes
- Organize favorites and create custom collections
- Share recipes with a community of fellow mixologists
- Track ingredients and learn about different spirits and mixers

StirCraft bridges the gap between inspiration and creation, making it easy to explore the world of cocktails while building your personal mixology knowledge.

## ✨ Key Features

### 🔐 User Authentication & Profiles
- Secure user registration and login
- Personalized user profiles with location and preferences
- Age verification (21+) for responsible service

### 🍹 Comprehensive Cocktail Management
- **Discover**: Browse over 500+ cocktails from TheCocktailDB API
- **Create**: Build custom cocktail recipes with detailed ingredients
- **Edit**: Modify and perfect your recipes
- **Organize**: Add cocktails to custom lists and favorites

### 📋 Smart List Management
- **Favorites**: One-click favoriting system
- **Your Creations**: Automatic collection of user-created recipes
- **Custom Lists**: Create themed collections (e.g., "Summer Cocktails", "Party Drinks")
- **Quick Actions**: Easy add/remove functionality

### 🥃 Ingredient & Vessel Database
- Extensive ingredient catalog with categorization
- Alcohol content tracking and calculations
- Glassware and vessel recommendations
- Smart measurement conversion

### 🎨 Modern, Responsive Design
- Clean, professional interface built with Bootstrap
- Mobile-responsive design for on-the-go access
- Intuitive navigation and user experience
- Accessibility-compliant design

## 🚀 Getting Started

### Try StirCraft
👉 **[Visit StirCraft Live Application](#)** *(Coming Soon)*

### Explore the Code
- 📋 **[View Planning Materials](docs/project-status.md)** - Project roadmap and current status
- 💻 **[GitHub Repository](https://github.com/General-Assembly-Team-1/stir-craft)** - Full source code
- 📚 **[Technical Documentation](docs/README.md)** - Developer setup guide

## 🛠️ Technologies Used

### Backend
- **Python 3.12** - Core programming language
- **Django 5.2.5** - Web framework for rapid development
- **PostgreSQL** - Robust database for data persistence
- **Django REST Framework** - API development (future enhancement)

### Frontend
- **HTML5 & CSS3** - Modern web standards
- **Bootstrap 5** - Responsive design framework
- **Django Templates** - Server-side rendering
- **JavaScript** - Interactive user experiences

### External Integrations
- **TheCocktailDB API** - Cocktail recipe data source
- **django-taggit** - Flexible tagging system
- **Redis** - Caching and session management

### Deployment & DevOps
- **Heroku** - Cloud application hosting
- **Gunicorn** - Production WSGI server
- **WhiteNoise** - Static file serving
- **PostgreSQL** - Production database

## 🎯 Next Steps: Planned Enhancements

### User Experience
- **Recipe Ratings & Reviews** - Community-driven quality feedback
- **Advanced Search** - Filter by ingredients, difficulty, time to make
- **Recipe Recommendations** - AI-powered suggestions based on preferences
- **Social Features** - Follow other users and share recipe collections

### Technical Enhancements
- **Mobile App** - Native iOS and Android applications
- **Recipe Import/Export** - Import from popular cocktail apps and websites
- **Inventory Tracking** - Track your home bar ingredients
- **Shopping Lists** - Generate ingredient shopping lists for recipes

### Community Features
- **Recipe Comments** - Discussion and tips on recipes
- **Photo Uploads** - Share photos of your cocktail creations
- **Recipe Contests** - Monthly themed cocktail competitions
- **Expert Profiles** - Verified bartender and mixologist accounts

## 🏆 Project Attributions

### External Resources
- **[TheCocktailDB](https://www.thecocktaildb.com/)** - Comprehensive cocktail recipe database
- **[Bootstrap](https://getbootstrap.com/)** - CSS framework for responsive design
- **[Django](https://www.djangoproject.com/)** - High-level Python web framework
- **Icons from [Font Awesome](https://fontawesome.com/)** - Professional iconography

### Team
**General Assembly Team 1** - Full-stack development team specializing in Django web applications

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### 🍸 Ready to mix things up? Start exploring StirCraft today!

*Built with ❤️ by cocktail enthusiasts, for cocktail enthusiasts*

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

### 🔐 Environment Variables Setup (NEW!)

**IMPORTANT**: This project now uses secure environment variables for all secrets. Follow these steps carefully:

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Generate a new secret key:**
   ```bash
   pipenv run python -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())"
   ```

3. **Edit your .env file:**
   ```bash
   # Edit .env and replace the SECRET_KEY with the generated one
   # Update your database password if different from the default
   ```

4. **NEVER commit .env files:**
   - Your `.env` file contains secrets and is automatically ignored by git
   - Always use `.env.example` as a template for new environments
   - For production, use your platform's secret management (GitHub Actions secrets, AWS Parameter Store, etc.)

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
   # Enter a secure password when prompted (update your .env file with this password)
   
   sudo -u postgres createdb --owner=macfarley stircraft
   ```

3. **Update your .env file:**
   ```bash
   # Edit .env and set your actual database password
   DATABASE_URL=postgres://macfarley:your-actual-password@localhost:5432/stircraft
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

3. **Copy environment template:**
   ```bash
   cp .env.example .env
   # Then edit .env with your actual values (see above)
   ```

4. **Install dependencies:**
   ```bash
   pipenv install
   ```

5. **Activate the virtual environment:**
   ```bash
   pipenv shell
   ```

6. **Navigate to the Django project:**
   ```bash
   cd stircraft
   ```

7. **Apply database migrations:**
   ```bash
   # No need to export DB_PASSWORD - it's now read from .env automatically
   python manage.py migrate
   ```

8. **Seed the database with cocktail data:**
   ```bash
   # Import a small test batch (10 cocktails)  
   python manage.py seed_from_thecocktaildb --limit 10
   
   # Import 100 cocktails from all letters
   python manage.py seed_from_thecocktaildb --limit 100
   
   # Import ALL available cocktails (could be 500+)
   python manage.py seed_from_thecocktaildb
   ```

9. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

10. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

11. **Access the application:**
    - Main application: http://127.0.0.1:8000/
    - Admin interface: http://127.0.0.1:8000/admin/

### 🔒 Security Notes

#### For Development
- Always use `.env.example` as your template
- Generate a unique SECRET_KEY for your local environment
- Never commit your `.env` file to version control
- Use secure database passwords (not the ones shown in documentation)

#### For Production
- Use your platform's secret management system:
  - **GitHub Actions**: Repository secrets (Settings → Secrets and variables → Actions)
  - **Heroku**: Config vars (Settings → Config Vars)
  - **AWS**: Parameter Store or Secrets Manager
  - **Docker**: Environment variables or secret mounts
- Set `DEBUG=False` in production
- Use strong, unique passwords for all services
- Configure proper `ALLOWED_HOSTS` for your domain

#### For Team Collaboration
- Each team member should create their own `.env` file
- Share configuration requirements via `.env.example`
- Document any new environment variables in `.env.example`
- Use different database passwords for each developer

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

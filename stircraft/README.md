# 🍸 StirCraft: Professional Cocktail Recipe Manager

**A sophisticated Django web application for cocktail enthusiasts, bartenders, and culinary professionals.**

🌐 **Live Site**: [https://stircraft-app-0dd06cf5d30a.herokuapp.com/](https://stircraft-app-0dd06cf5d30a.herokuapp.com/)

## 🍸 Live Site Preview

![StirCraft Live Screenshot](stir_craft/static/images/StirCraftLiveScreenshot.png)
*StirCraft's elegant homepage showcasing speakeasy-inspired typography and intuitive cocktail discovery*

![Django](https://img.shields.io/badge/Django-4.2-green) ![Python](https://img.shields.io/badge/Python-3.12-blue) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple) ![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## 🎯 **What is StirCraft?**

StirCraft is a comprehensive cocktail recipe management platform that transforms how you discover, create, and share cocktail recipes. Built with Django and modern web technologies, it offers a rich set of features for both individual users and cocktail communities.

### ✨ **Core Features**

#### 🍹 **Recipe Management**
- **Create & Edit** custom cocktail recipes with precise measurements
- **Fork & Remix** existing recipes to create your own variations  
- **Rich Metadata** including ABV calculation, color classification, and preparation methods
- **Professional Images** with automatic optimization and responsive display
- **Intelligent Tagging** system for easy discovery and filtering

#### 👥 **Social Features**
- **User Profiles** with age verification and location tracking
- **Custom Lists** with themed collections and personalized curation
- **Favorites System** with cross-user discovery and sharing
- **Public Feed** for discovering new recipes from the community
- **Recipe Attribution** and forking history tracking

#### 🎨 **User Experience**
- **Responsive Design** optimized for desktop, tablet, and mobile
- **WCAG AA Accessibility** with high-contrast color scheme
- **Intuitive Interface** with modal overlays and AJAX interactions
- **Advanced Search** with multi-criteria filtering and tag-based discovery
- **Professional UI** with custom CSS framework and Bootstrap integration

#### 🛠️ **Advanced Features**
- **Bulk Operations** for efficient list management
- **Tag Management** for ingredients and cocktails
- **Dynamic Forms** with real-time validation and expansion
- **Professional Data Import** from TheCocktailDB API
- **Database Seeding** with realistic social data for presentations

---

## 🚀 **Quick Start**

### Prerequisites
- **Python 3.12+**
- **PostgreSQL 15+**
- **pip** or **pipenv**

### 1. **Database Setup**
```bash
# Create PostgreSQL user and database
sudo -u postgres psql -c "ALTER USER $(whoami) PASSWORD 'stircraft123';"
sudo -u postgres createdb --owner=$(whoami) stircraft
```

### 2. **Application Setup**
```bash
# Clone and install
git clone <repository-url>
cd stir-craft/stircraft

# Install dependencies
pipenv install

# Run migrations
DB_PASSWORD=stircraft123 pipenv run python manage.py migrate

# Create dynamic demo database (optional)
pipenv run python manage.py seed_dynamic_database --limit 100 --num-users 10

# Start development server
DB_PASSWORD=stircraft123 pipenv run python manage.py runserver
```

### 3. **Verify Setup**
Visit `http://127.0.0.1:8000` and explore the application with pre-loaded demo data.

---

## 🏗️ **Architecture Overview**

### **Technology Stack**
- **Backend**: Django 4.2 with PostgreSQL database
- **Frontend**: Bootstrap 5.3 with custom CSS framework
- **JavaScript**: Modern ES6+ with comprehensive test coverage
- **Images**: PIL/Pillow for processing and optimization
- **APIs**: TheCocktailDB integration for professional recipe data

---

## 📊 **Entity Relationship Diagram (ERD)**

![StirCraft ERD](staticfiles/images/ERD/StirCraft ERD.svg)
*Complete database schema showing relationships between all models*

---

## 🗄️ **Database Models Deep Dive**

### **👤 User System Models**

#### **User (Django Built-in)**
- **Purpose**: Authentication and basic user information
- **Fields**: username, email, password, first_name, last_name, date_joined
- **Relationships**: One-to-One with Profile, One-to-Many with Cocktail, List

#### **Profile**
- **Purpose**: Extended user information with age verification
- **Key Fields**:
  - `user` (OneToOneField to User)
  - `birthdate` (DateField with 21+ validation)
  - `location` (CharField for zip code)
  - `updated_at` (DateTimeField)
- **Business Logic**: Age verification for alcohol content compliance
- **Validation**: Custom clean() method ensures users are 21+

### **🧂 Recipe Component Models**

#### **Ingredient**
- **Purpose**: Individual components used in cocktail recipes
- **Key Fields**:
  - `name` (CharField, unique)
  - `ingredient_type` (CharField with 12 predefined choices)
  - `description` (TextField, optional)
  - `alcohol_content` (FloatField, 0-100% ABV)
  - `flavor_tags` (TaggableManager via django-taggit)
  - `created_at`, `updated_at` (DateTimeFields)
- **Types**: spirit, liqueur, wine, beer, mixer, soda, syrup, bitters, juice, dairy, garnish, other
- **Methods**: `is_alcoholic()` for age verification and mocktail filtering

#### **Vessel**
- **Purpose**: Glassware and serving containers
- **Key Fields**:
  - `name` (CharField, unique)
  - `vessel_type` (CharField with predefined choices)
  - `description` (TextField)
  - `volume_oz` (FloatField for capacity)
  - `is_stemmed` (BooleanField)
  - `material` (CharField)
- **Types**: rocks, highball, martini, coupe, wine, beer, shot, other
- **Usage**: Recipe presentation and proper serving recommendations

### **🍹 Core Recipe Models**

#### **Cocktail**
- **Purpose**: Complete cocktail recipes with metadata
- **Key Fields**:
  - `name` (CharField, unique per user)
  - `creator` (ForeignKey to User)
  - `description` (TextField)
  - `instructions` (TextField with preparation steps)
  - `image` (ImageField with upload_to)
  - `color` (CharField from predefined palette)
  - `prep_method` (CharField: shaken, stirred, built, blended, etc.)
  - `abv_percentage` (FloatField, calculated)
  - `vessel` (ForeignKey to Vessel)
  - `origin_story` (TextField, optional)
  - `is_public` (BooleanField, default True)
  - `forked_from` (ForeignKey to self, for recipe attribution)
  - `tags` (TaggableManager)
  - `created_at`, `updated_at` (DateTimeFields)
- **Business Logic**: 
  - Automatic ABV calculation from ingredients
  - Recipe forking with attribution tracking
  - Public/private visibility control
- **Methods**: `calculate_abv()`, `get_total_volume()`, `get_ingredient_list()`

#### **RecipeComponent**
- **Purpose**: Junction table linking cocktails to ingredients with quantities
- **Key Fields**:
  - `cocktail` (ForeignKey to Cocktail)
  - `ingredient` (ForeignKey to Ingredient)
  - `quantity` (DecimalField with validation)
  - `unit` (CharField: oz, dash, splash, etc.)
  - `preparation_note` (CharField, optional)
  - `order` (IntegerField for ingredient sequence)
- **Units**: oz, ml, dash, splash, pinch, drop, garnish, rim, float
- **Validation**: Positive quantities, unit compatibility
- **Usage**: Enables precise recipe measurements and scaling

### **📁 Organization & Social Models**

#### **List**
- **Purpose**: User-curated cocktail collections
- **Key Fields**:
  - `name` (CharField)
  - `creator` (ForeignKey to User)
  - `description` (TextField, optional)
  - `cocktails` (ManyToManyField to Cocktail)
  - `is_public` (BooleanField, default False)
  - `created_at`, `updated_at` (DateTimeFields)
- **Features**:
  - Public/private visibility
  - Bulk operations (add/remove multiple cocktails)
  - List copying and sharing
- **Methods**: `get_cocktail_count()`, `copy_to_user()`

### **💾 Social Features (Many-to-Many Through User)**
- **Favorites**: User ↔ Cocktail relationship via User.cocktail_favorites
- **Following**: Future User ↔ User relationship (planned)
- **Ratings**: Future User ↔ Cocktail rating system (planned)

---

## 🛣️ **URL Structure & Routing**

### **🏠 General Navigation**
```python
''                          # Homepage with featured cocktails
'dashboard/'                # User dashboard with statistics
'about/'                    # About page
```

### **🔑 Authentication**
```python
'sign-up/'                  # User registration with age verification
'sign-in/'                  # User login
'sign-out/'                 # User logout
```

### **👤 User Profiles**
```python
'profile/'                  # Current user's profile
'profile/<int:user_id>/'    # View other user's profile
'profile/update/'           # Edit profile information
```

### **🍹 Cocktail Management**
```python
'cocktails/'                           # Browse all cocktails
'cocktails/<int:cocktail_id>/'         # View cocktail detail
'cocktails/create/'                    # Create new cocktail
'cocktails/<int:fork_from_id>/fork/'   # Fork existing recipe
'cocktails/<int:cocktail_id>/edit/'    # Edit cocktail
'cocktails/<int:cocktail_id>/delete/'  # Delete cocktail
```

### **📁 List Management**
```python
'lists/'                               # User's personal lists
'lists/create/'                        # Create new list
'lists/manage/'                        # Bulk list operations
'lists/<int:list_id>/'                 # View list detail
'lists/<int:list_id>/edit/'            # Edit list
'lists/<int:list_id>/delete/'          # Delete list
'lists/<int:list_id>/copy/'            # Copy list to current user
'users/<int:user_id>/lists/'           # View another user's lists
```

### **🌐 Public & Social Features**
```python
'public/'                              # Public feed of lists
'public/<int:list_id>/'                # View public list detail
```

### **🎯 AJAX API Endpoints**
```python
# List Operations
'cocktails/<int:cocktail_id>/add-to-list/<int:list_id>/'        # Add to specific list
'cocktails/<int:cocktail_id>/quick-add-to-list/'               # Quick-add modal
'cocktails/<int:cocktail_id>/remove-from-list/<int:list_id>/'  # Remove from list
'lists/<int:list_id>/bulk-operations/'                         # Bulk add/remove
'lists/user-lists-json/'                                       # JSON endpoint for lists

# Social Features
'cocktails/<int:cocktail_id>/favorite/'                        # Toggle favorite status
'cocktails/<int:cocktail_id>/quick-add/'                      # Quick-add modal

# Tag Management
'cocktails/<int:cocktail_id>/add-tag/'                        # Add tag to cocktail
'cocktails/<int:cocktail_id>/remove-tag/'                     # Remove tag from cocktail
'ingredients/<int:ingredient_id>/add-flavor-tag/'             # Add flavor tag to ingredient
```

### **🥃 Ingredient & Vessel Management**
```python
'ingredients/'                         # Browse ingredients
'ingredients/<int:ingredient_id>/'     # Ingredient detail
'ingredients/create/'                  # Add new ingredient
'ingredients/check-duplicates/'        # AJAX duplicate checking

'vessels/'                            # Browse glassware
'vessels/<int:pk>/'                   # Vessel detail (Class-based view)
```

---

## 🔧 **Key Technical Patterns**

### **URL Naming Conventions**
- **Resource-based**: `/cocktails/`, `/lists/`, `/ingredients/`
- **RESTful actions**: `/create/`, `/edit/`, `/delete/`
- **Hierarchical relationships**: `/users/<id>/lists/`
- **AJAX endpoints**: Clear action verbs like `/toggle-favorite/`

### **View Architecture**
- **Function-based views**: Most CRUD operations and complex business logic
- **Class-based views**: Simple detail views (VesselDetailView)
- **AJAX views**: Return JSON for dynamic frontend interactions
- **Authentication**: Login required for most create/edit operations

### **Data Relationships**
- **One-to-One**: User ↔ Profile (extended user info)
- **One-to-Many**: User → Cocktails, User → Lists, Cocktail → RecipeComponents
- **Many-to-Many**: List ↔ Cocktails, User ↔ Cocktails (favorites)
- **Many-to-Many Through**: Cocktail ↔ Ingredients (via RecipeComponent)
- **Self-referential**: Cocktail.forked_from (recipe attribution)

### **Business Logic Highlights**
- **ABV Calculation**: Automatic from ingredient alcohol content and quantities
- **Age Verification**: 21+ validation on profile creation
- **Recipe Attribution**: Fork tracking maintains original creator credit
- **Tag System**: Flexible categorization via django-taggit
- **Bulk Operations**: Efficient multi-cocktail list management

---

## 📱 **Feature Showcase**

### **Dashboard Experience**
- **Personalized Welcome** with user-specific statistics
- **Quick Actions** for creating recipes and managing lists
- **Recent Activity** feed with your latest creations
- **Discovery Section** with trending and recommended cocktails

### **Recipe Creation**
- **Multi-Step Forms** with ingredient management and validation
- **Dynamic Components** that expand as you add ingredients
- **Professional Formatting** with measurement standardization
- **Image Upload** with automatic resizing and optimization

### **Social Discovery**
- **Public Feed** showcasing community creations
- **User Profiles** with public recipe collections
- **List Sharing** with copy and remix functionality
- **Tag-Based Discovery** for finding recipes by mood, ingredient, or style

### **Advanced Management**
- **Bulk List Operations** for efficient organization
- **Tag Management** for both recipes and ingredients
- **Fork Tracking** to maintain recipe attribution
- **Professional Data Import** for building comprehensive databases

---

## 🎭 **Demo Data & Presentation Ready**

StirCraft includes a sophisticated demo data system perfect for presentations:

### **Dynamic User Generation**
```bash
# Create 15 themed users with realistic profiles
python manage.py seed_dynamic_database --num-users 15

# Sample users: ShakenNotNerd, NegroniBaloney, BittersAndBytes, etc.
```

### **Themed Collections**
- **🧪 Technical**: "Test Tubes & Tinctures", "The Debugger's Daiquiris"
- **🎭 Fantasy**: "Villainous Vintages", "Elixirs of Enchantment"  
- **🌈 Inclusive**: "Zero-Proof, 100% Joy", "Cheers to Queers"
- **🧊 Seasonal**: "Summer Slammers", "Sweater Weather Sips"

### **Realistic Social Interactions**
- **316 Total Favorites** distributed naturally across users
- **53 Custom Lists** with theme-appropriate cocktail curation
- **87 Cross-User Favorites** simulating organic discovery patterns
- **209 Professional Cocktails** with high-quality images and metadata

---

## 🧪 **Testing & Quality Assurance**

### **Comprehensive Test Suite**
```bash
# Run all tests
./scripts/run_tests.sh

# Current status: 57/57 tests passing
# Coverage: Models, Views, Forms, JavaScript, and Integration
```

### **Test Categories**
- ✅ **Model Tests**: Data validation, relationships, and business logic
- ✅ **View Tests**: Authentication, permissions, and response validation  
- ✅ **Form Tests**: Input validation, error handling, and security
- ✅ **JavaScript Tests**: UI interactions, AJAX calls, and user experience
- ✅ **Integration Tests**: End-to-end workflow validation

### **Quality Standards**
- **Code Coverage**: Comprehensive test coverage across all components
- **Accessibility**: WCAG AA compliance with high-contrast design
- **Performance**: Optimized queries and efficient asset delivery
- **Security**: Input validation, CSRF protection, and secure authentication

---

## 📁 **Project Structure**

```
stircraft/
├── manage.py                          # Django management interface
├── stir_craft/                        # Main application package
│   ├── models.py                      # Database models (6 core models)
│   ├── views.py                       # View controllers (35+ views)
│   ├── urls.py                        # URL routing configuration
│   ├── admin.py                       # Django admin customization
│   ├── forms/                         # Form definitions
│   │   ├── cocktail_forms.py         # Recipe creation and editing
│   │   ├── list_forms.py              # List management
│   │   └── profile_forms.py           # User profile and authentication
│   ├── templates/                     # HTML templates
│   │   ├── base/                      # Base templates and layout
│   │   ├── cocktails/                 # Recipe views and forms
│   │   ├── lists/                     # List management interface
│   │   ├── users/                     # Profile and authentication
│   │   ├── partials/                  # Reusable template components
│   │   └── errors/                    # Error pages
│   ├── static/                        # Static assets
│   │   ├── css/                       # Custom CSS framework
│   │   ├── js/                        # JavaScript components
│   │   └── images/                    # Application images
│   ├── management/commands/           # Custom Django commands
│   │   ├── seed_dynamic_database.py   # Demo data generation
│   │   ├── seed_from_thecocktaildb.py # Professional data import
│   │   └── [10 other specialized commands]
│   ├── tests/                         # Test suite
│   │   ├── test_models.py             # Model testing
│   │   ├── test_views.py              # View testing
│   │   ├── test_forms.py              # Form testing
│   │   └── test_javascript.py         # JavaScript testing
│   └── migrations/                    # Database migrations
├── stircraft/                         # Django project settings
│   ├── settings.py                    # Application configuration
│   ├── urls.py                        # Root URL configuration
│   └── wsgi.py                        # WSGI application entry point
├── media/                             # User-uploaded content
├── staticfiles/                       # Collected static files for production
├── docs/                              # Technical documentation
└── scripts/                           # Development and deployment scripts
```

---

## 🚀 **Production Deployment**

StirCraft is production-ready with:

### **Deployment Features**
- ✅ **Heroku Compatibility** with Procfile and requirements.txt
- ✅ **Environment Variables** for secure configuration management
- ✅ **Static File Management** with WhiteNoise for efficient delivery
- ✅ **Database Migrations** with PostgreSQL production setup
- ✅ **Error Handling** with custom error pages and logging

### **Security Features**
- ✅ **CSRF Protection** on all forms and AJAX requests
- ✅ **User Authentication** with secure password requirements
- ✅ **Age Verification** for alcohol-related content
- ✅ **Input Validation** at model, form, and view levels
- ✅ **SQL Injection Prevention** through Django ORM

### **Performance Optimizations**
- ✅ **Efficient Queries** with select_related and prefetch_related
- ✅ **Image Optimization** with automatic resizing and compression
- ✅ **CSS/JS Minification** for faster page loads
- ✅ **Database Indexing** on frequently queried fields

---

## 🔧 **Development & Contribution**

### **Development Workflow**
```bash
# Daily development
./scripts/run_tests.sh              # Run test suite
pipenv run python manage.py runserver   # Start development server

# Database management
python manage.py seed_dynamic_database   # Generate demo data
python manage.py migrate                 # Apply database changes
```

### **Code Standards**
- **PEP 8 Compliance** for Python code formatting
- **Django Best Practices** for models, views, and templates
- **Modern JavaScript** with ES6+ features and testing
- **Semantic HTML** with accessibility considerations
- **Component-Based CSS** with variables and modular organization

### **Documentation**
Comprehensive technical documentation available in the `docs/` folder:
- **[Quick Setup Guide](./docs/quick-setup.md)** - Get running in 10 minutes
- **[Development Guide](./docs/development-guide.md)** - Coding standards and workflow
- **[Testing Infrastructure](./docs/testing-infrastructure.md)** - Test framework details
- **[Deployment Guide](./docs/deployment-guide.md)** - Production deployment instructions

---

## 🏆 **Perfect for**

### **General Assembly Presentations**
- **Complex Data Relationships** showcasing Django ORM mastery
- **Professional UI/UX** with responsive design and accessibility
- **Social Features** demonstrating user interaction patterns
- **Real-time Functionality** with AJAX and dynamic content
- **Production-Ready Code** with testing, documentation, and deployment

### **Portfolio Showcase**
- **Full-Stack Development** with Django, PostgreSQL, and modern JavaScript
- **Professional Design** with custom CSS framework and Bootstrap
- **Complex Business Logic** including recipe calculations and social features
- **Data Management** with API integration and advanced seeding
- **Quality Assurance** with comprehensive testing and documentation

### **Professional Use**
- **Restaurant Industry** for menu planning and recipe standardization
- **Bartending Schools** for educational curriculum and training
- **Cocktail Enthusiasts** for personal recipe collection and sharing
- **Event Planning** for beverage menu creation and management

---

## 📊 **Project Statistics**

- **6 Core Database Models** with advanced relationships
- **35+ Views** covering all CRUD operations and social features
- **40+ Template Components** with modular, reusable design
- **12 Management Commands** for data management and automation
- **57 Comprehensive Tests** with 100% critical path coverage
- **209 Sample Cocktails** with professional images and metadata
- **15+ Demo Users** with realistic social interaction patterns
- **53 Themed Lists** showcasing content curation capabilities

---

## 🎉 **Get Started Today**

Ready to explore the art of cocktail creation? StirCraft combines the precision of professional bartending with the convenience of modern web technology.

```bash
git clone <repository-url>
cd stir-craft/stircraft
pipenv install
DB_PASSWORD=stircraft123 pipenv run python manage.py migrate
pipenv run python manage.py seed_dynamic_database
DB_PASSWORD=stircraft123 pipenv run python manage.py runserver
```

**Visit:** `http://127.0.0.1:8000`  
**Demo Login:** Any of the seeded users with password `stircraft2024`

---

## 🚀 **Future Enhancements**

### **Planned Next Features**

#### **Enhanced Social Features** 
- **User Following System**: Follow favorite creators and get notifications
- **Recipe Reviews & Ratings**: Community-driven quality assessment
- **Enhanced Social Feed**: Activity stream with user interactions
- **Recipe Collaboration**: Multiple users contributing to recipes

#### **Advanced Recipe Management**
- **Recipe Versioning**: Track changes and maintain history
- **Batch Scaling Calculator**: Scale recipes for events (1 drink → 50 servings)
- **Ingredient Substitutions**: AI-powered alternative suggestions
- **Nutritional Information**: Calorie counting and dietary restrictions

#### **Professional Tools**
- **Bar Inventory Management**: Track ingredient stock levels
- **Cost Calculation**: Recipe profitability for commercial use
- **Menu Generation**: Export professional PDF menus
- **QR Code Integration**: Link physical menus to digital recipes

#### **Mobile & API Expansion**
- **Progressive Web App**: Offline recipe access
- **REST API**: Third-party integration capabilities
- **Mobile Applications**: Native iOS/Android applications
- **Voice Interface**: Smart assistant integration

---

## 📞 **Support & Contact**

For questions, feature requests, or contributions:
- **Technical Documentation**: [./docs/README.md](./docs/README.md)
- **Issue Tracking**: GitHub Issues
- **Development Team**: General Assembly Team 1
- **Testing Reports**: Available in `stircraft/stir_craft/tests/htmlcov/index.html`

---

*StirCraft: Where technology meets mixology.* 🥂

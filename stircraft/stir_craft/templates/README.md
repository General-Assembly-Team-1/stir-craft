# StirCraft Templates Guide

## Overview

StirCraft uses Django's templating system with a structured approach to template organization, partials, and CSS management. All styling has been moved out of templates into the `/static/css/` folder.

## Template Structure

```
stircraft/stir_craft/templates/
├── base.html                    # Master layout template
├── dashboard.html              # User dashboard with personalized content
├── registration/               # Authentication templates
│   ├── login.html              # User login form
│   ├── register.html           # User registration form
│   └── password_reset.html     # Password reset functionality
├── cocktails/                  # Cocktail-related templates
│   ├── create.html             # Cocktail creation form
│   ├── detail.html             # Individual cocktail display
│   ├── edit.html               # Cocktail editing form
│   └── favorites.html          # User's favorite cocktails
├── ingredients/                # Ingredient management
│   ├── create.html             # Add new ingredients
│   ├── detail.html             # Ingredient information
│   └── list.html               # All ingredients listing
├── lists/                      # Custom cocktail lists
│   ├── create.html             # Create new list
│   ├── detail.html             # View list contents
│   ├── edit.html               # Edit list properties
│   └── management.html         # Manage multiple lists
├── vessels/                    # Glassware templates
│   ├── create.html             # Add new vessel types
│   └── list.html               # All vessel types
├── about/                      # Static pages
│   └── about.html              # About page content
└── partials/                   # Reusable template components
    ├── cocktail_card.html      # Individual cocktail display
    ├── cocktail_form_row.html  # Form ingredient rows
    ├── ingredient_row.html     # Ingredient display component
    ├── list_card.html          # List preview component
    ├── navigation.html         # Site navigation
    ├── pagination.html         # Page navigation controls
    └── toast_messages.html     # User feedback notifications
```

## Base Template System

### Master Layout (`base.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- CSS Loading Order (Critical) -->
    <link rel="stylesheet" href="{% static 'css/variables.css' %}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
    
    <!-- Page-specific CSS -->
    {% block extra_css %}{% endblock %}
    
    <title>{% block title %}StirCraft{% endblock %}</title>
</head>
<body>
    <!-- Navigation -->
    {% include 'partials/navigation.html' %}
    
    <!-- Main Content -->
    <main class="container-fluid">
        {% include 'partials/toast_messages.html' %}
        {% block content %}{% endblock %}
    </main>
    
    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### CSS Loading Strategy
**Critical**: `variables.css` must load first to provide CSS custom properties for all other stylesheets.

```html
<!-- 1. Variables (CSS custom properties) -->
<link rel="stylesheet" href="{% static 'css/variables.css' %}">

<!-- 2. Bootstrap framework -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- 3. Base application styles -->
<link rel="stylesheet" href="{% static 'css/base.css' %}">

<!-- 4. Page-specific styles -->
{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/cocktail.css' %}">
{% endblock %}
```

## Template Inheritance Pattern

### Standard Page Template
```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Page Title - StirCraft{% endblock %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/specific-page.css' %}">
{% endblock %}

{% block content %}
<div class="page-container">
    <h1 class="page-title">Page Content</h1>
    
    <!-- Include reusable partials -->
    {% include 'partials/cocktail_card.html' with cocktail=cocktail %}
</div>
{% endblock %}

{% block extra_js %}
    <script src="{% static 'js/page-specific.js' %}"></script>
{% endblock %}
```

## Partial Templates

### Cocktail Card (`partials/cocktail_card.html`)
**Purpose**: Reusable cocktail display component used across multiple pages

```html
<div class="cocktail-card" data-cocktail-id="{{ cocktail.id }}">
    <div class="cocktail-card-header">
        <h3 class="cocktail-name">{{ cocktail.name }}</h3>
        {% if user.is_authenticated %}
            <button class="favorite-btn" 
                    data-cocktail-id="{{ cocktail.id }}"
                    data-favorited="{% if cocktail.id in user_favorites %}true{% else %}false{% endif %}">
                <i class="fas fa-heart {% if cocktail.id not in user_favorites %}far{% endif %}"></i>
            </button>
        {% endif %}
    </div>
    
    <div class="cocktail-card-body">
        {% if cocktail.image %}
            <img src="{{ cocktail.image.url }}" alt="{{ cocktail.name }}" class="cocktail-image">
        {% endif %}
        
        <div class="cocktail-details">
            <p class="instructions">{{ cocktail.instructions|truncatewords:15 }}</p>
            <div class="cocktail-meta">
                <span class="ingredient-count">{{ cocktail.ingredients.count }} ingredients</span>
                <span class="creator">By {{ cocktail.creator.username }}</span>
            </div>
        </div>
    </div>
    
    <div class="cocktail-card-actions">
        <a href="{% url 'cocktail_detail' cocktail.id %}" class="btn btn-primary">View Recipe</a>
        {% if user == cocktail.creator %}
            <a href="{% url 'cocktail_edit' cocktail.id %}" class="btn btn-secondary">Edit</a>
        {% endif %}
    </div>
</div>
```

**Usage**:
```html
{% include 'partials/cocktail_card.html' with cocktail=cocktail %}
```

### Form Row Component (`partials/cocktail_form_row.html`)
**Purpose**: Dynamic ingredient input rows for cocktail creation/editing

```html
<div class="ingredient-row" data-row-id="{{ forloop.counter0 }}">
    <div class="row align-items-center">
        <div class="col-md-4">
            {{ form.ingredient }}
        </div>
        <div class="col-md-3">
            {{ form.amount }}
        </div>
        <div class="col-md-3">
            {{ form.unit }}
        </div>
        <div class="col-md-2">
            <button type="button" class="remove-ingredient-btn btn btn-outline-danger btn-sm">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>
</div>
```

### Navigation (`partials/navigation.html`)
**Purpose**: Consistent site navigation with authentication-aware content

```html
<nav class="navbar navbar-expand-lg">
    <div class="container-fluid">
        <a class="navbar-brand" href="{% url 'dashboard' %}">
            <img src="{% static 'images/logo.png' %}" alt="StirCraft" class="navbar-logo">
            StirCraft
        </a>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto">
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'dashboard' %}">Dashboard</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'cocktail_create' %}">Create Cocktail</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'ingredient_list' %}">Ingredients</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'favorites' %}">Favorites</a>
                </li>
            </ul>
            
            <ul class="navbar-nav">
                {% if user.is_authenticated %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                            {{ user.username }}
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{% url 'profile' %}">Profile</a></li>
                            <li><a class="dropdown-item" href="{% url 'list_management' %}">My Lists</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{% url 'logout' %}">Logout</a></li>
                        </ul>
                    </li>
                {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'login' %}">Login</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'register' %}">Register</a>
                    </li>
                {% endif %}
            </ul>
        </div>
    </div>
</nav>
```

## Form Templates

### Dynamic Form Handling
StirCraft uses Django formsets for dynamic ingredient management in cocktail forms.

```html
<!-- cocktails/create.html -->
{% extends 'base.html' %}
{% load static %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/forms.css' %}">
    <link rel="stylesheet" href="{% static 'css/cocktail.css' %}">
{% endblock %}

{% block content %}
<div class="form-container">
    <h1>Create New Cocktail</h1>
    
    <form method="post" enctype="multipart/form-data" id="cocktail-form">
        {% csrf_token %}
        
        <!-- Basic cocktail information -->
        <div class="form-section">
            <h3>Cocktail Details</h3>
            {{ form.name.label_tag }}
            {{ form.name }}
            
            {{ form.instructions.label_tag }}
            {{ form.instructions }}
            
            {{ form.image.label_tag }}
            {{ form.image }}
        </div>
        
        <!-- Dynamic ingredient formset -->
        <div class="form-section">
            <h3>Ingredients</h3>
            <div id="ingredient-formset">
                {{ ingredient_formset.management_form }}
                {% for form in ingredient_formset %}
                    {% include 'partials/cocktail_form_row.html' with form=form %}
                {% endfor %}
            </div>
            
            <button type="button" id="add-ingredient" class="btn btn-secondary">
                <i class="fas fa-plus"></i> Add Ingredient
            </button>
        </div>
        
        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Create Cocktail</button>
            <a href="{% url 'dashboard' %}" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}

{% block extra_js %}
    <script src="{% static 'js/cocktail-form.js' %}"></script>
{% endblock %}
```

## Data Injection for JavaScript

### Configuration Injection
Templates pass server-side data to JavaScript through JSON script tags:

```html
<!-- In base.html or specific templates -->
{{ block.super }}
<script>
    window.stirCraftConfig = {
        csrfToken: '{{ csrf_token }}',
        urls: {
            addToFavorites: '{% url "add_to_favorites" %}',
            removeFromFavorites: '{% url "remove_from_favorites" %}',
            searchCocktails: '{% url "cocktail_search" %}'
        },
        user: {
            isAuthenticated: {% if user.is_authenticated %}true{% else %}false{% endif %},
            username: '{% if user.is_authenticated %}{{ user.username }}{% endif %}'
        }
    };
</script>
```

## Template Organization Best Practices

### File Naming Conventions
- **Action-based**: `create.html`, `edit.html`, `detail.html`
- **Purpose-based**: `dashboard.html`, `favorites.html`
- **Partial prefix**: All partials in `/partials/` folder

### CSS Organization
- **No inline styles**: All styling moved to CSS files
- **No `<style>` blocks**: Use external stylesheets only
- **Component-specific**: Each template can load specific CSS via `{% block extra_css %}`

### JavaScript Integration
- **External files only**: No inline JavaScript in templates
- **Configuration injection**: Use JSON script tags for server data
- **Event delegation**: Handle dynamic content through event bubbling

## Responsive Design Patterns

### Mobile-First Approach
```html
<div class="cocktail-grid">
    <!-- Responsive grid using Bootstrap classes -->
    {% for cocktail in cocktails %}
        <div class="col-12 col-md-6 col-lg-4 mb-4">
            {% include 'partials/cocktail_card.html' with cocktail=cocktail %}
        </div>
    {% endfor %}
</div>
```

### Accessibility Considerations
```html
<!-- Semantic HTML structure -->
<main role="main">
    <h1 id="page-title">Cocktail Collection</h1>
    
    <!-- Skip navigation for screen readers -->
    <a href="#main-content" class="skip-link">Skip to main content</a>
    
    <!-- ARIA labels for interactive elements -->
    <button class="favorite-btn" 
            aria-label="Add {{ cocktail.name }} to favorites"
            aria-pressed="false">
        <i class="fas fa-heart" aria-hidden="true"></i>
    </button>
</main>
```

## Performance Optimization

### Template Caching
```python
# In views.py
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def cocktail_list(request):
    cocktails = Cocktail.objects.select_related('creator').prefetch_related('ingredients')
    return render(request, 'cocktails/list.html', {'cocktails': cocktails})
```

### Asset Loading
```html
<!-- Preload critical resources -->
<link rel="preload" href="{% static 'css/variables.css' %}" as="style">
<link rel="preload" href="{% static 'fonts/custom-font.woff2' %}" as="font" type="font/woff2" crossorigin>

<!-- Defer non-critical JavaScript -->
<script src="{% static 'js/analytics.js' %}" defer></script>
```

---

**All templates follow this structured approach with external styling and progressive enhancement through JavaScript.**

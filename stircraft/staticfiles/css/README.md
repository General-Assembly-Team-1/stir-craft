# StirCraft CSS Architecture

## File Organization

```
static/css/
├── variables.css      # 🎨 Design system tokens and color variables
├── base.css          # 🏗️ Global styles and reusable components
├── dashboard.css     # 📊 Dashboard-specific styling
├── cocktail.css      # 🍹 Cocktail pages and components
├── forms.css         # 📝 Form styling across the application
├── auth.css          # 🔐 Authentication pages
├── about.css         # ℹ️ About and static pages
├── ingredients.css   # 🥃 Ingredient-specific styling
├── lists.css         # 📋 List management interfaces
└── vessels.css       # 🥃 Vessel selection and display
```

## Architecture Principles

### 1. **Variables-First Design**
All CSS files import `variables.css` first to ensure consistent design tokens:

```css
/* Required at the top of every CSS file */
@import url('variables.css');

/* Then use variables instead of hardcoded values */
.component {
    background-color: var(--primary-color);
    border: 1px solid var(--border-color);
    padding: var(--spacing-md);
}
```

### 2. **Component-Based Organization**
- **Global components** → `base.css`
- **Page-specific styles** → dedicated files (e.g., `dashboard.css`)
- **Feature-specific styles** → component files (e.g., `forms.css`)

### 3. **No Hardcoded Values**
Use CSS variables for all design tokens:
- ❌ `color: #007bff;`
- ✅ `color: var(--primary-color);`

## Design System (variables.css)

### Color Variables

#### Primary Brand Colors
```css
--primary-color: #007bff;        /* Main brand blue */
--primary-dark: #0056b3;         /* Darker blue for hover */
--primary-light: #66b3ff;        /* Light accent blue */
--primary-alpha-05: rgba(0, 123, 255, 0.05); /* Transparent primary */
```

#### Semantic Colors
```css
--success-color: #28a745;        /* Success green */
--danger-color: #dc3545;         /* Error red */
--warning-color: #ffc107;        /* Warning yellow */
--info-color: #17a2b8;          /* Info teal */
```

#### Text Colors
```css
--text-primary: #212529;         /* Main text */
--text-secondary: #6c757d;       /* Secondary text */
--text-muted: #8e9194;          /* Muted text */
```

#### Background Colors
```css
--bg-white: #ffffff;
--bg-light: #f8f9fa;
--card-bg: #ffffff;
--card-bg-hover: #f8f9fa;
```

#### Spacing & Layout
```css
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;    /* 24px */
--spacing-xl: 3rem;      /* 48px */
```

#### Visual Effects
```css
--border-radius: 0.375rem;
--border-radius-lg: 0.5rem;
--card-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
--card-shadow-hover: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
--transition-fast: all 0.15s ease-in-out;
```

### Flavor Tag System
Specialized variables for cocktail flavor tags:
```css
--flavor-sweet-bg: #fff3cd;
--flavor-sweet-text: #856404;
--flavor-sour-bg: #d1ecf1;
--flavor-sour-text: #0c5460;
/* ... and more flavor combinations */
```

## File-Specific Guidelines

### variables.css
- **Purpose**: Single source of truth for all design tokens
- **Content**: Only CSS custom properties (variables)
- **Usage**: Imported by all other CSS files

### base.css
- **Purpose**: Global styles and reusable components
- **Content**: 
  - Shared component styles (cards, buttons, lists)
  - Utility classes
  - Global overrides
- **Scope**: Used across multiple pages

### Page-Specific Files
- **dashboard.css**: Dashboard layout, stats cards, action grids
- **cocktail.css**: Cocktail cards, detail pages, flavor tags
- **forms.css**: Form styling, input groups, validation states
- **auth.css**: Login, signup, profile pages

## Adding New Styles

### 1. Choose the Right File
```
Global component → base.css
Page-specific → create new file (e.g., search.css)
Feature-specific → existing component file
```

### 2. Follow the Template
```css
/* Always start with variables import */
@import url('variables.css');

/* Page/Component-specific styles */
.new-component {
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: var(--spacing-md);
    transition: var(--transition-fast);
}

.new-component:hover {
    background-color: var(--card-bg-hover);
    box-shadow: var(--card-shadow-hover);
}
```

### 3. Update Template
```html
<!-- In Django template -->
{% block extra_css %}
{% load static %}
<link href="{% static 'css/new-component.css' %}" rel="stylesheet">
{% endblock %}
```

## Responsive Design

### Mobile-First Approach
```css
/* Base styles for mobile */
.component {
    padding: var(--spacing-sm);
    font-size: 0.875rem;
}

/* Tablet and up */
@media (min-width: 768px) {
    .component {
        padding: var(--spacing-md);
        font-size: 1rem;
    }
}

/* Desktop and up */
@media (min-width: 1024px) {
    .component {
        padding: var(--spacing-lg);
    }
}
```

### Bootstrap Integration
StirCraft uses Bootstrap 5 as the foundation:
- Use Bootstrap classes for layout (grid, flexbox)
- Override with custom variables for consistent theming
- Add component-specific styling in dedicated files

## Performance Optimization

### CSS Loading Strategy
1. **Bootstrap** (CDN) - Foundation styles
2. **variables.css** - Design system
3. **base.css** - Global components
4. **page-specific.css** - Only when needed

### File Size Management
- Keep variables.css focused on tokens only
- Split large files by logical components
- Use CSS custom properties for theme variations
- Leverage browser caching for static files

## Development Workflow

### 1. Design Token Changes
Edit `variables.css` → All components update automatically

### 2. New Component
1. Create component styles in appropriate file
2. Use existing variables where possible
3. Add new variables to `variables.css` if needed
4. Test across different pages and themes

### 3. Refactoring Existing Styles
1. Identify hardcoded values
2. Replace with appropriate variables
3. Test for consistency across components
4. Update in both development and production files

## Browser Support

- **Modern browsers**: Full CSS custom properties support
- **IE 11**: Fallback values provided where needed
- **Mobile browsers**: Optimized for touch interfaces
- **Performance**: Efficient loading and caching strategies

---

**For more details on color management, see [docs/css-organization.md](../../../docs/css-organization.md)**

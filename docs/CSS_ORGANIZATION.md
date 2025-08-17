# CSS Organization for StirCraft

This document outlines the CSS organization strategy for the StirCraft project, following best practices for maintainability and reusability.

## File Structure

```
static/css/
├── base.css        # Global styles, partial components, utility classes
└── dashboard.css   # Dashboard-specific styles
```

## CSS Architecture

### 1. `base.css` - Global & Component Styles

**Purpose**: Contains styles that are reused across multiple pages and templates.

**Sections**:
- **Global Styles**: Card hover effects, button transitions, link styles
- **Gradient Styles**: Consistent gradient definitions (e.g., primary gradient)
- **Profile Components**: Avatar styling, reusable across profile pages
- **Cocktail Card Components**: General cocktail card styling for lists
- **List Item Components**: Reusable list item patterns
- **Empty State Components**: Consistent empty state styling
- **Quick Actions Components**: Button styling for action grids
- **Locked Element Styles**: Styling for disabled/locked elements
- **Responsive Utilities**: Mobile-first responsive adjustments
- **Utility Classes**: Helper classes like text truncation, border variants

### 2. `dashboard.css` - Page-Specific Styles

**Purpose**: Contains styles specific only to the dashboard page.

**Sections**:
- **Dashboard Layout**: Overall page structure and spacing
- **Stats Display**: User statistics component styling
- **Creation List Styles**: Styles specific to the "Your Creations" section
- **Favorites Styles**: Dashboard favorites section styling
- **List Overview Styles**: Dashboard list overview styling
- **Dashboard Quick Actions**: Large button grid specific to dashboard
- **Badge Styles**: Dashboard-specific badge styling
- **Responsive Dashboard**: Mobile adaptations for dashboard layout

## Design Principles

### 1. **Separation of Concerns**
- **No inline styles** in templates
- **Component-specific** CSS in base.css
- **Page-specific** CSS in dedicated files

### 2. **Reusability**
- Common components styled once in base.css
- Consistent naming conventions
- Modular class structure

### 3. **Maintainability**
- Organized sections with clear comments
- Consistent spacing and formatting
- CSS custom properties for theme colors

### 4. **Performance**
- CSS files loaded based on need
- Minimal redundancy between files
- Efficient selectors

## Class Naming Conventions

### Component Classes
- `.profile-avatar` - Profile avatar styling
- `.cocktail-card` - General cocktail card styling
- `.list-item` - Generic list item styling
- `.empty-state` - Empty state containers
- `.quick-action-btn` - Quick action buttons

### State Classes
- `.locked-indicator` - Visual indication of locked elements
- `.btn-locked` - Disabled button styling
- `.stats-value` - Statistical value styling
- `.stats-label` - Statistical label styling

### Layout Classes
- `.dashboard-container` - Dashboard page container
- `.dashboard-header` - Dashboard header section
- `.dashboard-action-buttons` - Header action button group
- `.quick-actions-grid` - Grid layout for quick actions

### Utility Classes
- `.text-truncate-2` - Truncate text to 2 lines
- `.text-truncate-3` - Truncate text to 3 lines
- `.border-start-*` - Colored left borders
- `.badge-count` - Consistent badge spacing

## Template Integration

### Base Template
```django
<!-- Bootstrap CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">

<!-- StirCraft Base Styles -->
{% load static %}
<link href="{% static 'css/base.css' %}" rel="stylesheet">

{% block extra_css %}{% endblock %}
```

### Page-Specific Templates
```django
{% block extra_css %}
{% load static %}
<link href="{% static 'css/dashboard.css' %}" rel="stylesheet">
{% endblock %}
```

## Benefits

1. **Maintainability**: Styles are organized logically and easy to find
2. **Performance**: Only necessary CSS is loaded per page
3. **Consistency**: Reusable components ensure design consistency
4. **Scalability**: Easy to add new pages without style conflicts
5. **Team Collaboration**: Clear structure makes it easy for teams to work together

## Future Considerations

- **Theme System**: Could extend to support multiple themes
- **CSS Variables**: Could add more CSS custom properties for theming
- **Component Library**: Could evolve into a full component library
- **Build Process**: Could add CSS preprocessing (Sass/Less) if needed
- **Critical CSS**: Could implement critical CSS extraction for performance

## File Loading Strategy

- **base.css**: Loaded on every page via base template
- **page-specific.css**: Loaded only when needed via `{% block extra_css %}`
- **Vendor CSS**: Bootstrap and Bootstrap Icons loaded from CDN
- **Order**: Vendor → Base → Page-specific for proper cascade

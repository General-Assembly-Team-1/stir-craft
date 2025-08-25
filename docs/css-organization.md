# CSS Organization for StirCraft

This document outlines the CSS organization strategy for the StirCraft project, following best practices for maintainability and reusability.

## File Structure

```
static/css/
├── variables.css   # 🎨 Color variables & design system tokens
├── base.css        # Global styles, partial components, utility classes  
├── dashboard.css   # Dashboard-specific styles
├── cocktail.css    # Cocktail-specific styles
├── forms.css       # Form styling
├── ingredients.css # Ingredient-specific styles
├── lists.css       # List management styles
└── vessels.css     # Vessel-specific styles
```

## CSS Architecture

### 0. `variables.css` - Design System & Color Management

**Purpose**: Central location for all design tokens including colors, spacing, shadows, and transitions.

**Sections**:
- **Color Variables**: Primary, semantic, text, and background colors
- **Spacing & Layout**: Consistent spacing units and layout tokens
- **Visual Effects**: Shadows, borders, and border radius values
- **Transitions**: Consistent animation timing and easing
- **Typography**: Font sizes, weights, and line heights
- **Component Tokens**: Variables specific to components like flavor tags

**Usage**: All other CSS files should `@import url('variables.css');` at the top and use `var(--variable-name)` instead of hardcoded values.

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

### 3. Page-Specific CSS Files

**Purpose**: Each major page or component group has its own CSS file for organization and performance.

- **`cocktail.css`**: Cocktail detail pages, flavor tags, rating systems
- **`forms.css`**: Form styling including cocktail creation and editing forms
- **`ingredients.css`**: Ingredient-specific styling and components
- **`lists.css`**: List management interfaces and list-specific components
- **`vessels.css`**: Vessel selection and display components
- **`auth.css`**: Authentication pages (login, register, profile)
- **`about.css`**: About and static page styling

### File Organization Rules

1. **Variables First**: All CSS files must import `variables.css` first
2. **No Hardcoded Values**: Use CSS variables for colors, spacing, shadows, etc.
3. **Component Scope**: Styles should be scoped to avoid conflicts
4. **Page Specificity**: Only include page-specific styles in dedicated files
5. **Shared Components**: Common components go in `base.css`

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
- **CSS custom properties for all design tokens**
- **Central color management via variables.css**
- **Consistent naming conventions across files**

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

<!-- StirCraft Design System & Base Styles -->
{% load static %}
<link href="{% static 'css/variables.css' %}" rel="stylesheet">
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

- **variables.css**: Loaded first on every page for design tokens
- **base.css**: Loaded on every page via base template for shared components
- **page-specific.css**: Loaded only when needed via `{% block extra_css %}`
- **Vendor CSS**: Bootstrap and Bootstrap Icons loaded from CDN
- **Order**: Vendor → Variables → Base → Page-specific for proper cascade

## Color Management Integration

This CSS organization works hand-in-hand with our color management system:

1. **variables.css** contains all color definitions and design tokens
2. **All other CSS files** import variables.css and use `var(--color-name)`
3. **No hardcoded colors** anywhere except in variables.css
4. **Consistent theming** across all pages and components

For detailed color usage guidelines, see [Color Management System Documentation](color-management-system.md).

## CSS Audit Checklist

When reviewing or adding CSS files, ensure:

- [ ] **Variables imported**: `@import url('variables.css');` at the top
- [ ] **No hardcoded colors**: Use `var(--color-name)` instead of hex/rgb values
- [ ] **Proper file location**: Page-specific styles in dedicated files
- [ ] **Component reusability**: Shared components in base.css
- [ ] **Template integration**: Proper loading via base template or `{% block extra_css %}`
- [ ] **No inline styles**: All styling moved to appropriate CSS files
- [ ] **Consistent naming**: Follow established naming conventions
- [ ] **Responsive design**: Mobile-first approach with proper breakpoints

---

# Color Management System

## 🎨 How CSS Variables Work

The color management system uses CSS Custom Properties (CSS Variables) which provide:
- **Consistent theming** across all components
- **Easy maintenance** - change colors in one place
- **Browser native support** - no build tools required
- **Dynamic updates** - can be changed with JavaScript if needed

## 🔧 Using Color Variables

### In CSS Files

```css
/* Import variables at the top of your CSS file */
@import url('variables.css');

/* Use variables instead of hardcoded colors */
.my-component {
    background-color: var(--primary-color);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    transition: all var(--transition-fast);
}

.my-component:hover {
    background-color: var(--primary-dark);
    box-shadow: var(--card-shadow-hover);
}
```

### Available Variables

#### Primary Colors
- `--primary-color` - Main brand blue (#007bff)
- `--primary-dark` - Darker blue for hover states
- `--primary-light` - Lighter blue for accents
- `--primary-alpha-05` - Semi-transparent primary (5% opacity)

#### Semantic Colors
- `--success-color`, `--success-dark`, `--success-light`
- `--danger-color`, `--danger-dark`, `--danger-light`  
- `--warning-color`, `--warning-dark`, `--warning-light`
- `--info-color`, `--info-dark`, `--info-light`

#### Text Colors
- `--text-primary` - Main text color
- `--text-secondary` - Secondary text color
- `--text-muted` - Muted text color

#### Background Colors
- `--bg-white`, `--bg-light`, `--bg-lighter`
- `--bg-gray-100`, `--bg-gray-200`, `--bg-gray-300`

#### Borders & Effects
- `--border-color`, `--border-light`, `--border-dark`
- `--card-shadow`, `--card-shadow-hover`
- `--border-radius`, `--border-radius-lg`

#### Flavor Tags
- `--flavor-sweet-bg/text`, `--flavor-sour-bg/text`, etc.

## 🎨 Updating Colors

To change the color scheme:

1. **Edit `variables.css`** - Update the color values in the `:root` section
2. **Colors update automatically** across all files using the variables
3. **No need to update individual CSS files**

### Example: Changing Primary Color

```css
/* In variables.css */
:root {
    /* Change from blue to green theme */
    --primary-color: #28a745;        /* New green primary */
    --primary-dark: #1e7e34;         /* Darker green */
    --primary-light: #6fbf73;        /* Lighter green */
    --primary-alpha-05: rgba(40, 167, 69, 0.05);
}
```

All components using `var(--primary-color)` will automatically use the new green color!

## 🔄 Migrating Existing Styles

To convert hardcoded colors to variables:

1. **Find hardcoded colors:**
   ```css
   /* Before */
   .component {
       background: #007bff;
       border: 1px solid #dee2e6;
   }
   ```

2. **Replace with variables:**
   ```css
   /* After */
   .component {
       background: var(--primary-color);
       border: 1px solid var(--border-color);
   }
   ```

## 📝 Color Management Best Practices

1. **Always use variables** for colors, spacing, and common values
2. **Import variables first** in each CSS file
3. **Use semantic names** when adding new variables
4. **Group related variables** together in variables.css
5. **Test changes** across different pages to ensure consistency
- [ ] **Responsive design**: Mobile-first approach with proper breakpoints

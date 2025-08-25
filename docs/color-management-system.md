# StirCraft Color Management System

## Overview

This document explains how to use the CSS variables system for maintaining consistent colors across the StirCraft application, similar to Sass variables but using native CSS custom properties.

## 🎨 How It Works

The color management system uses CSS Custom Properties (CSS Variables) which provide:
- **Consistent theming** across all components
- **Easy maintenance** - change colors in one place
- **Browser native support** - no build tools required
- **Dynamic updates** - can be changed with JavaScript if needed

## 📁 File Structure

```
stir_craft/static/css/
├── variables.css     # 🎨 Color variables & design system
├── base.css         # 🏗️ Base styles using variables
├── cocktail.css     # 🍹 Cocktail-specific styles
├── dashboard.css    # 📊 Dashboard styles
└── [other files]    # Other component styles
```

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

### Example Usage

```css
/* Button styling with variables */
.btn-stircraft {
    background-color: var(--primary-color);
    color: var(--bg-white);
    border-radius: var(--border-radius);
    transition: all var(--transition-fast);
}

.btn-stircraft:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

/* Card styling */
.custom-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--border-radius-lg);
    box-shadow: var(--card-shadow);
}
```

## 🚀 Adding New CSS Files

When creating new CSS files:

1. **Import variables first:**
   ```css
   @import url('variables.css');
   ```

2. **Use variables instead of hardcoded values:**
   ```css
   /* ❌ Don't do this */
   .component { color: #007bff; }
   
   /* ✅ Do this */
   .component { color: var(--primary-color); }
   ```

3. **Include in templates:**
   ```html
   {% load static %}
   <link href="{% static 'css/your-new-file.css' %}" rel="stylesheet">
   ```

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

## 🌙 Future Enhancements

The system is ready for:
- **Dark mode support** (uncomment dark mode section in variables.css)
- **Theme switching** with JavaScript
- **Component-specific color overrides**
- **CSS-in-JS integration** if needed

## 📝 Best Practices

1. **Always use variables** for colors, spacing, and common values
2. **Import variables first** in each CSS file
3. **Use semantic names** when adding new variables
4. **Group related variables** together in variables.css
5. **Test changes** across different pages to ensure consistency

## 🆚 Comparison with Sass

| Feature | CSS Variables | Sass Variables |
|---------|--------------|----------------|
| Browser Support | Native | Requires compilation |
| Build Tools | None needed | Requires Sass compiler |
| Dynamic Changes | ✅ Runtime updates | ❌ Compile-time only |
| Cascading | ✅ Follows CSS cascade | ❌ Compile-time substitution |
| Performance | ✅ No build step | ⚠️ Requires build process |

For Django projects, CSS variables provide the same benefits as Sass variables with less complexity!

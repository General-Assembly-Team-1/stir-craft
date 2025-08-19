# StirCraft Template Partials Guide

## 📋 Overview

This guide explains how to use and create template partials in the StirCraft project. Template partials work like React components - they're reusable pieces of HTML that help keep our templates clean, maintainable, and DRY (Don't Repeat Yourself).

## 🎯 Why Use Template Partials?

### Before Partials
- **cocktail_detail.html**: 180+ lines of complex HTML
- Hard to read and understand
- Difficult to maintain
- Code duplication across templates
- Team members stepping on each other's changes

### After Partials
- **cocktail_detail.html**: ~40 clean, readable lines
- Each component has a single purpose
- Easy to reuse across templates
- Multiple team members can work on different components
- Much easier to debug and modify

## 📁 Current Partials Structure

```
templates/stir_craft/partials/
├── _cocktail_header.html          # Cocktail name + edit buttons
├── _cocktail_meta.html            # Creator, date, alcohol %, volume
├── _ingredients_table.html        # Complete ingredients table
├── _user_lists_card.html         # "Your Lists" sidebar card
├── _ingredient_details_card.html  # Ingredient details sidebar
└── _quick_actions_card.html      # Action buttons sidebar
```

## 🔧 How to Use Partials

### Basic Usage
```django
<!-- Include a partial in any template -->
{% include 'stir_craft/partials/_cocktail_header.html' %}
```

### Passing Additional Context
```django
<!-- Pass extra variables to a partial -->
{% include 'stir_craft/partials/_ingredients_table.html' with components=custom_components %}

<!-- Pass multiple variables -->
{% include 'stir_craft/partials/_cocktail_meta.html' with show_stats=True highlight_creator=False %}
```

### Real Example
```django
<!-- cocktail_detail.html (simplified) -->
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-lg-8">
            <div class="card">
                {% include 'stir_craft/partials/_cocktail_header.html' %}
                <div class="card-body">
                    {% include 'stir_craft/partials/_cocktail_meta.html' %}
                    {% include 'stir_craft/partials/_ingredients_table.html' %}
                </div>
            </div>
        </div>
        <div class="col-lg-4">
            {% include 'stir_craft/partials/_user_lists_card.html' %}
            {% include 'stir_craft/partials/_ingredient_details_card.html' %}
            {% include 'stir_craft/partials/_quick_actions_card.html' %}
        </div>
    </div>
</div>
{% endblock %}
```

## 🆕 Creating New Partials

### When to Create a Partial
- Template section is used in multiple places
- Template becomes too long (>100 lines)
- Section has a clear, single purpose
- You want to improve readability

### Step-by-Step Process

#### 1. Identify the Section
Look for HTML blocks that:
- Serve a single purpose
- Could be reused elsewhere
- Make the template hard to read

#### 2. Create the Partial File
```bash
# Create in partials directory with underscore prefix
touch templates/stir_craft/partials/_my_component.html
```

#### 3. Extract the HTML
Move the HTML section to your new partial file:
```django
<!-- _my_component.html -->
<div class="my-component">
    <h4>{{ title }}</h4>
    <p>{{ description }}</p>
    <!-- Rest of component HTML -->
</div>
```

#### 4. Replace in Original Template
```django
<!-- Original template -->
<!-- Replace the long HTML block with: -->
{% include 'stir_craft/partials/_my_component.html' %}
```

#### 5. Test Thoroughly
- Load the page and verify it looks the same
- Test with different data
- Check responsive behavior
- Test in different browsers

### Naming Conventions
- **File name**: Start with underscore (`_component_name.html`)
- **Descriptive**: Name should clearly indicate purpose
- **Lowercase**: Use lowercase with underscores
- **Location**: Always in `templates/app_name/partials/`

## 🔄 Reusing Partials Across Templates

### Example: Cocktail Cards in List View
```django
<!-- cocktail_index.html -->
{% for cocktail in cocktails %}
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            {% include 'stir_craft/partials/_cocktail_header.html' %}
            <div class="card-body">
                <!-- List-specific content -->
                <p class="card-text">{{ cocktail.description|truncatewords:20 }}</p>
                <a href="{% url 'cocktail_detail' cocktail.id %}" class="btn btn-primary">View Recipe</a>
            </div>
        </div>
    </div>
{% endfor %}
```

### Example: Dashboard Widgets
```django
<!-- dashboard.html -->
<div class="row">
    <div class="col-md-6">
        {% include 'stir_craft/partials/_user_lists_card.html' %}
    </div>
    <div class="col-md-6">
        {% include 'stir_craft/partials/_quick_actions_card.html' %}
    </div>
</div>
```

## 🧪 Testing Partials

### What to Test
- **Visual**: Component renders correctly
- **Context**: Works with different data
- **Responsive**: Looks good on mobile/desktop
- **Accessibility**: Screen reader friendly
- **Cross-browser**: Works in different browsers

### Testing Checklist
- [ ] Component renders without errors
- [ ] All required context variables are available
- [ ] Optional context variables have sensible defaults
- [ ] Bootstrap classes work correctly
- [ ] Links and buttons function properly
- [ ] Responsive design works on mobile

## 👥 Team Collaboration Guidelines

### Working with Partials
1. **Check existing partials** before creating new ones
2. **Communicate** when modifying shared partials
3. **Test thoroughly** after changes
4. **Document** any new context requirements

### Code Review Focus
- Ensure single responsibility principle
- Check for proper Bootstrap usage
- Verify accessibility standards
- Confirm responsive design

### Git Workflow
```bash
# Create feature branch for partial work
git checkout -b feature/new-partial

# Create/modify partials
# Test thoroughly

# Commit with descriptive message
git add templates/stir_craft/partials/
git commit -m "Add user profile card partial"

# Push and create PR
git push origin feature/new-partial
```

## 🚨 Common Pitfalls and Solutions

### Problem: Partial Not Rendering
**Cause**: Wrong file path or typo in include statement
**Solution**: Double-check path and filename spelling

### Problem: Missing Variables
**Error**: `VariableDoesNotExist` or empty content
**Solution**: Ensure all required context is available or add default values

### Problem: Styling Issues
**Cause**: Bootstrap classes not working or CSS conflicts
**Solution**: Check that base.html includes Bootstrap CSS

### Problem: Partial Too Complex
**Symptom**: Partial doing too many things
**Solution**: Break it down into smaller, focused partials

## 📈 Future Enhancements

### Planned Improvements
- **Component Library**: Catalog of all available partials
- **Smart Defaults**: Partials that work without explicit context
- **Theme Support**: Partials that adapt to different themes
- **Performance**: Cached partials for better performance

### Advanced Patterns
```django
<!-- Conditional partials -->
{% if user.is_authenticated %}
    {% include 'stir_craft/partials/_user_actions.html' %}
{% else %}
    {% include 'stir_craft/partials/_guest_actions.html' %}
{% endif %}

<!-- Looped partials -->
{% for ingredient in cocktail.ingredients %}
    {% include 'stir_craft/partials/_ingredient_card.html' with ingredient=ingredient %}
{% endfor %}
```

## 📚 Additional Resources

### Django Documentation
- [Template Tags: include](https://docs.djangoproject.com/en/stable/ref/templates/builtins/#include)
- [Template Context](https://docs.djangoproject.com/en/stable/topics/templates/#variables)

### Best Practices
- Keep partials focused on single responsibility
- Use meaningful names and comments
- Test with various context data
- Consider accessibility from the start

---

## 🤝 Questions or Issues?

If you run into problems with partials or have ideas for new ones:
1. Check this guide first
2. Look at existing partials for examples
3. Ask the team in our chat
4. Create an issue in our GitHub repo

Remember: The goal is to make our templates **easier to read, maintain, and reuse**. When in doubt, create a partial!

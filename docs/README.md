````markdown
# StirCraft Documentation

Welcome to the StirCraft documentation hub. This directory contains comprehensive guides for developers, testers, and contributors working on the StirCraft cocktail management application.

## Documentation Structure

### Core Development Guides
- **[Development Guide](development-guide.md)** - Complete setup, development workflow, and environment configuration
- **[Deployment Guide](deployment-guide.md)** - Production deployment to Heroku with PostgreSQL

### Code Architecture
- **[CSS Organization](css-organization.md)** - CSS architecture, variables system, and styling standards
- **[JavaScript Organization](javascript-organization.md)** - Frontend architecture, AJAX patterns, and event handling
- **[File Organization](file-organization-audit.md)** - Project structure and file organization standards

### Feature Implementation
- **[Cocktail Forms Technical Guide](cocktail-forms-technical-guide.md)** - Dynamic forms, formsets, and validation
- **[Image Handling Implementation](image-handling-implementation-guide.md)** - File uploads, processing, and optimization

### Database & Infrastructure
- **[PostgreSQL Setup](postgres-setup.md)** - Database configuration for development and production

## Component-Specific Documentation

For detailed technical documentation, see component-specific README files:

- **[CSS Documentation](/static/css/README.md)** - Detailed CSS architecture, variables, and component styles
- **[JavaScript Documentation](/static/js/README.md)** - Frontend components, utilities, and interaction patterns  
- **[Template Documentation](/templates/README.md)** - Template structure, partials, and organization
- **[Testing Documentation](/tests/README.md)** - Comprehensive testing infrastructure and best practices

## Quick Navigation

### For New Developers
1. Start with [Development Guide](development-guide.md) for initial setup
2. Review [CSS Organization](css-organization.md) for styling architecture
3. Check [Testing Documentation](/tests/README.md) for running tests

### For Deployment
1. Follow [Deployment Guide](deployment-guide.md) for production setup
2. Reference [PostgreSQL Setup](postgres-setup.md) for database configuration

### For Feature Development
1. Review [Cocktail Forms Technical Guide](cocktail-forms-technical-guide.md) for form patterns
2. Check [JavaScript Documentation](/static/js/README.md) for frontend patterns
3. Use [Image Handling Implementation](image-handling-implementation-guide.md) for file uploads

## Project Overview

StirCraft is a Django-based cocktail management application that allows users to:
- Create and manage cocktail recipes
- Organize ingredients and measurements  
- Build custom cocktail lists
- Share and discover cocktail recipes
- Manage favorites and personal collections

### Technology Stack
- **Backend**: Django 5.2.5, PostgreSQL
- **Frontend**: Bootstrap 5, Custom CSS with CSS Variables, Vanilla JavaScript
- **Deployment**: Heroku with PostgreSQL add-on
- **Testing**: Django TestCase, Jest for JavaScript

### Key Features
- Dynamic cocktail form with ingredient management
- User authentication and profile management
- Image upload and optimization
- Responsive design with mobile-first approach
- AJAX-powered favorites and list management
- Comprehensive search and filtering

## Contributing

### Code Standards
- Follow PEP 8 for Python code
- Use CSS custom properties for consistent theming
- Implement progressive enhancement for JavaScript features
- Write comprehensive tests for all new features

### Development Workflow
1. Create feature branch from `main`
2. Implement feature with tests
3. Run full test suite: `./scripts/run_tests.sh`
4. Submit pull request with documentation updates

### Documentation Standards
- Update relevant documentation for code changes
- Include code examples in technical guides
- Maintain clear section organization
- Test all code snippets and commands

## Architecture Overview

### Django Application Structure
```
stircraft/
├── stir_craft/           # Main application
│   ├── models.py         # Data models
│   ├── views.py          # View logic
│   ├── forms/            # Form definitions
│   ├── templates/        # HTML templates
│   ├── static/           # CSS, JS, images
│   └── tests/            # Test suite
└── stircraft/            # Project configuration
    ├── settings.py       # Django settings
    └── urls.py           # URL routing
```

### Frontend Architecture
- **CSS**: Variables-based theming with component-specific files
- **JavaScript**: Modular approach with event delegation
- **Templates**: Django templates with reusable partials

### Database Design
- User-centric design with profile management
- Flexible ingredient and measurement system
- Optimized for cocktail recipe relationships

---

*This documentation is actively maintained. For questions or improvements, please refer to the [Development Guide](development-guide.md) for contribution guidelines.*

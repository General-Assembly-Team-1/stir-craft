# Django Sass Integration Example

## Option 2: Using django-sass for real Sass support

If you prefer Sass over CSS variables, here's how to set it up:

### 1. Install django-sass
```bash
pip install django-sass
```

### 2. Add to INSTALLED_APPS
```python
# settings.py
INSTALLED_APPS = [
    'django_sass',
    # ... other apps
]
```

### 3. Create Sass files
```scss
// stir_craft/static/scss/_variables.scss
$primary-color: #007bff;
$primary-dark: #0056b3;
$success-color: #28a745;
$danger-color: #dc3545;

$border-radius: 0.375rem;
$transition-fast: 0.15s ease-in-out;

// Text colors
$text-primary: #212529;
$text-secondary: #6c757d;

// Background colors  
$bg-light: #f8f9fa;
$bg-white: #ffffff;
```

```scss
// stir_craft/static/scss/base.scss
@import 'variables';

.card {
    border: none;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    transition: box-shadow $transition-fast;
    
    &:hover {
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    }
}

.btn-primary {
    background-color: $primary-color;
    border-color: $primary-color;
    
    &:hover {
        background-color: $primary-dark;
        border-color: $primary-dark;
    }
}
```

### 4. Configure django-sass
```python
# settings.py
SASS_PROCESSOR_ROOT = os.path.join(BASE_DIR, 'stir_craft', 'static')
SASS_PROCESSOR_ENABLED = True
SASS_OUTPUT_STYLE = 'compressed'  # for production
```

### 5. Use in templates
```html
{% load sass_tags %}
<link href="{% sass_src 'scss/base.scss' %}" rel="stylesheet">
```

## Option 3: Node.js Build Process

### package.json
```json
{
  "scripts": {
    "build-css": "sass stircraft/stir_craft/static/scss:stircraft/stir_craft/static/css --watch",
    "build-css-prod": "sass stircraft/stir_craft/static/scss:stircraft/stir_craft/static/css --style=compressed"
  },
  "devDependencies": {
    "sass": "^1.50.0"
  }
}
```

### Run during development
```bash
npm run build-css
```

## Option 4: CSS Preprocessor with Django-Compressor

```python
# settings.py
INSTALLED_APPS = [
    'compressor',
    # ... other apps
]

COMPRESS_PRECOMPILERS = (
    ('text/scss', 'sass --scss {infile} {outfile}'),
)
```

```html
{% load compress %}
{% compress css %}
<link rel="stylesheet" type="text/scss" href="{% static 'scss/base.scss' %}">
{% endcompress %}
```

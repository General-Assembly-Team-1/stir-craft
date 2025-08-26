# 🗄️ Database Architecture & Management Commands

Complete guide to StirCraft's PostgreSQL database design, Django models, migrations, and custom management commands.

## 📊 **Database Overview**

StirCraft uses PostgreSQL 15+ with Django ORM for a robust, scalable data architecture supporting complex cocktail relationships and user-generated content.

### **Core Entities**
- **Users & Profiles** - Authentication and user preferences
- **Cocktails & Recipes** - Drink definitions with dynamic ingredients
- **Ingredients & Vessels** - Component library with categorization
- **Lists & Organization** - User collections and favorites
- **Tagging System** - Flexible categorization with django-taggit

## 🏗️ **Model Architecture**

### **User System Models**

#### **Profile Model**
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Social features
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Relationships**: One-to-one with Django User, connected to all user-generated content

### **Recipe System Models**

#### **Cocktail Model**
```python
class Cocktail(models.Model):
    # Basic information
    name = models.CharField(max_length=200)
    instructions = models.TextField()
    description = models.TextField(blank=True)
    
    # Categorization
    is_alcoholic = models.BooleanField(default=True)
    vessel = models.ForeignKey(Vessel, on_delete=models.SET_NULL, null=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='amber')
    
    # User relations
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    forked_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    
    # External data
    thecocktaildb_id = models.CharField(max_length=10, unique=True, null=True)
    attribution_text = models.CharField(max_length=200, blank=True)
    attribution_url = models.URLField(blank=True)
    
    # Media
    image = models.ImageField(upload_to='cocktails/', null=True, blank=True)
    
    # Tagging
    vibe_tags = TaggableManager(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Features**:
- **Forking System** - Users can create variations of existing cocktails
- **External Integration** - Links to TheCocktailDB for professional recipes
- **Dynamic Tagging** - Flexible categorization with mood/style tags
- **Attribution Tracking** - Credit for recipe sources

#### **Ingredient Model**
```python
class Ingredient(models.Model):
    CATEGORY_CHOICES = [
        ('spirit', 'Spirit'),
        ('liqueur', 'Liqueur'),
        ('mixer', 'Mixer'),
        ('garnish', 'Garnish'),
        ('syrup', 'Syrup'),
        ('bitters', 'Bitters'),
        ('fruit', 'Fruit'),
        ('herb', 'Herb/Spice'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    abv = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # External reference
    thecocktaildb_id = models.CharField(max_length=10, unique=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
```

**Categories**: Organized system for different ingredient types with ABV tracking for spirits

#### **RecipeComponent Model**
```python
class RecipeComponent(models.Model):
    UNIT_CHOICES = [
        ('oz', 'Ounce'),
        ('ml', 'Milliliter'),
        ('dash', 'Dash'),
        ('splash', 'Splash'),
        ('wedge', 'Wedge'),
        ('wheel', 'Wheel'),
        ('sprig', 'Sprig'),
        ('pinch', 'Pinch'),
        ('whole', 'Whole'),
        ('drop', 'Drop'),
        ('tsp', 'Teaspoon'),
        ('tbsp', 'Tablespoon'),
    ]
    
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE, related_name='recipe_components')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, blank=True)
    preparation_note = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = ('cocktail', 'ingredient')
```

**Features**: Flexible measurement system supporting various units and preparation notes

### **Organization System Models**

#### **Vessel Model**
```python
class Vessel(models.Model):
    VESSEL_TYPES = [
        ('rocks', 'Rocks Glass'),
        ('highball', 'Highball Glass'),
        ('martini', 'Martini Glass'),
        ('coupe', 'Coupe Glass'),
        ('wine', 'Wine Glass'),
        ('shot', 'Shot Glass'),
        ('mug', 'Mug'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    vessel_type = models.CharField(max_length=20, choices=VESSEL_TYPES)
    description = models.TextField(blank=True)
    capacity_oz = models.DecimalField(max_digits=5, decimal_places=2, null=True)
```

#### **List Model**
```python
class List(models.Model):
    LIST_TYPES = [
        ('favorites', 'Favorites'),
        ('custom', 'Custom List'),
        ('to_try', 'To Try'),
        ('collection', 'Collection'),
    ]
    
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    list_type = models.CharField(max_length=20, choices=LIST_TYPES, default='custom')
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    is_deletable = models.BooleanField(default=True)
    cocktails = models.ManyToManyField(Cocktail, related_name='in_lists', blank=True)
    forked_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = [['creator', 'name'], ['creator', 'list_type']]
```

**Features**: Supports different list types with forking capabilities and privacy controls

## 📋 **Migration History**

### **Database Evolution**

Our migration history shows the progressive development of the data model:

#### **Initial Setup (0001_initial.py)**
- Created core models: Profile, Ingredient, Vessel, Cocktail, RecipeComponent, List
- Established basic relationships and constraints
- Set up django-taggit integration

#### **List System Enhancements (0002, 0012, 0013)**
- **0002**: Added `is_deletable` field and improved unique constraints
- **0012**: Refined list uniqueness rules for better UX
- **0013**: Added forking capability to lists

#### **Ingredient System Improvements (0007, 0008)**
- **0007**: Updated ingredient type choices for better categorization
- **0008**: Refined ingredient categories with more granular options

#### **Visual & Attribution Features (0005, 0006, 0009, 0010, 0011)**
- **0005-0006**: Added image upload capability for cocktails
- **0009-0010**: Implemented color system with predefined choices
- **0011**: Added attribution tracking for recipe sources

#### **Forking System (0004)**
- Added `forked_from` field to enable cocktail variations
- Supports recipe evolution and community contributions

#### **Auto-generated Optimizations (0003, 0014)**
- Django-generated migrations for model refinements
- Performance optimizations and constraint improvements

### **Current Schema State**

```sql
-- Key tables and relationships
COCKTAIL (id, name, instructions, creator_id, vessel_id, forked_from_id, ...)
├── RECIPE_COMPONENT (cocktail_id, ingredient_id, amount, unit, ...)
├── INGREDIENT (id, name, category, abv, ...)
├── VESSEL (id, name, vessel_type, capacity_oz, ...)
└── LIST_COCKTAIL (list_id, cocktail_id) -- Many-to-many

LIST (id, name, creator_id, list_type, forked_from_id, ...)
PROFILE (id, user_id, bio, location, ...)
TAGGIT_TAG (id, name, slug)
TAGGIT_TAGGEDITEM (tag_id, object_id, content_type_id)
```

## ⚙️ **Management Commands**

StirCraft includes 12 custom Django management commands for database operations, data import, and maintenance.

### **Data Import & Seeding**

#### **seed_dynamic_database.py** 🌟
**Purpose**: Generate realistic demo data with themed users and diverse cocktails

**Usage**:
```bash
pipenv run python manage.py seed_dynamic_database [--users N] [--cocktails N]
```

**Features**:
- Creates themed user profiles (craft bartender, mixology student, etc.)
- Generates 200+ cocktails with proper ingredient relationships
- Imports data from TheCocktailDB API for professional recipes
- Creates realistic user lists and favorites
- Assigns appropriate tags and categories

**Output Example**:
```
✅ Created 15 themed users with realistic profiles
✅ Imported 209 cocktails from TheCocktailDB
✅ Generated 847 recipe components with proper measurements
✅ Created 45 user lists with appropriate cocktails
✅ Applied 156 vibe tags across cocktails
```

#### **seed_from_thecocktaildb.py**
**Purpose**: Import professional cocktail recipes from TheCocktailDB API

**Usage**:
```bash
pipenv run python manage.py seed_from_thecocktaildb [--limit N]
```

**Features**:
- Fetches cocktail data from external API
- Creates ingredients and vessels as needed
- Handles measurement unit conversions
- Preserves external attribution information

### **Data Quality & Maintenance**

#### **fix_ingredients.py**
**Purpose**: Standardize ingredient names and resolve duplicates

**Usage**:
```bash
pipenv run python manage.py fix_ingredients [--dry-run]
```

**Operations**:
- Removes duplicate ingredients
- Standardizes naming conventions
- Updates recipe component references
- Preserves data integrity during cleanup

#### **standardize_units.py**
**Purpose**: Convert measurements to consistent units

**Usage**:
```bash
pipenv run python manage.py standardize_units [--target-unit oz|ml]
```

**Features**:
- Converts between ounces and milliliters
- Handles special units (dash, splash, etc.)
- Maintains measurement accuracy
- Updates all recipe components

#### **fix_alcohol_content.py**
**Purpose**: Calculate and update ABV for ingredients and cocktails

**Usage**:
```bash
pipenv run python manage.py fix_alcohol_content
```

**Features**:
- Sets ABV for known spirits and liqueurs
- Calculates cocktail alcohol content
- Updates ingredient categories based on ABV

### **Categorization & Organization**

#### **recategorize_ingredients.py**
**Purpose**: Organize ingredients into proper categories

**Usage**:
```bash
pipenv run python manage.py recategorize_ingredients
```

**Categories Applied**:
- Spirits (whiskey, vodka, gin, etc.)
- Liqueurs (amaretto, cointreau, etc.)
- Mixers (tonic, soda, juices)
- Garnishes (lime, olives, etc.)
- Syrups and bitters

#### **detect_cocktail_vibes.py**
**Purpose**: Apply mood/style tags to cocktails

**Usage**:
```bash
pipenv run python manage.py detect_cocktail_vibes
```

**Vibe Categories**:
- **Mood**: refreshing, warming, elegant, fun
- **Occasion**: brunch, dinner, party, nightcap
- **Style**: classic, modern, tropical, creamy
- **Strength**: light, strong, smooth

#### **detect_cocktail_colors.py**
**Purpose**: Analyze and assign visual colors to cocktails

**Usage**:
```bash
pipenv run python manage.py detect_cocktail_colors
```

**Color Detection**:
- Analyzes ingredient combinations
- Assigns appropriate color category
- Supports filtering and visual organization

#### **normalize_colors.py**
**Purpose**: Standardize color values across the database

**Usage**:
```bash
pipenv run python manage.py normalize_colors
```

### **Cleanup & Optimization**

#### **cleanup_duplicate_ingredients.py**
**Purpose**: Remove exact duplicate ingredients and merge references

**Usage**:
```bash
pipenv run python manage.py cleanup_duplicate_ingredients [--dry-run]
```

**Operations**:
- Identifies exact name matches
- Merges recipe component references
- Removes orphaned ingredient records
- Maintains referential integrity

#### **clean_vibe_tags.py**
**Purpose**: Standardize and organize tagging system

**Usage**:
```bash
pipenv run python manage.py clean_vibe_tags
```

**Features**:
- Removes unused tags
- Standardizes tag names
- Groups related tags
- Optimizes tag relationships

#### **show_unit_examples.py**
**Purpose**: Display measurement examples for debugging

**Usage**:
```bash
pipenv run python manage.py show_unit_examples
```

**Output**: Lists all measurement units in use with example cocktails

### **Command Development Pattern**

All management commands follow this structure:

```python
from django.core.management.base import BaseCommand
from django.db import transaction

class Command(BaseCommand):
    help = 'Command description'
    
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--limit', type=int, default=100)
    
    def handle(self, *args, **options):
        with transaction.atomic():
            # Command logic here
            self.stdout.write(
                self.style.SUCCESS(f'✅ Operation completed')
            )
```

## 🔧 **Database Operations**

### **Common Database Tasks**

#### **Reset Database for Fresh Start**
```bash
# Drop and recreate database
pipenv run python manage.py dbshell
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
\q

# Apply all migrations
pipenv run python manage.py migrate

# Create superuser
pipenv run python manage.py createsuperuser

# Seed with demo data
pipenv run python manage.py seed_dynamic_database
```

#### **Backup and Restore**
```bash
# Create backup
pg_dump stircraft_db > backup.sql

# Restore from backup
psql stircraft_db < backup.sql
```

#### **Check Database State**
```bash
# View migration status
pipenv run python manage.py showmigrations

# Check for issues
pipenv run python manage.py check

# View database shell
pipenv run python manage.py dbshell
```

### **Performance Optimization**

#### **Database Indexes**
```python
# Key indexes in models
class Cocktail(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['creator', '-created_at']),
            models.Index(fields=['is_alcoholic', 'color']),
            models.Index(fields=['thecocktaildb_id']),
        ]

class RecipeComponent(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['cocktail', 'ingredient']),
        ]
```

#### **Query Optimization**
```python
# Efficient queries with select_related/prefetch_related
cocktails = Cocktail.objects.select_related(
    'creator', 'vessel', 'forked_from'
).prefetch_related(
    'recipe_components__ingredient',
    'vibe_tags',
    'in_lists'
)
```

### **Data Integrity**

#### **Constraint Enforcement**
- Unique cocktail names per creator
- Unique ingredient names globally
- Unique list names per user per type
- Foreign key cascading for data consistency

#### **Validation Rules**
- ABV values between 0-100%
- Amount values must be positive
- Required fields enforced at model level
- Custom validators for complex business rules

## 📊 **Database Statistics**

With full demo data seeded:

```
Users:           15 themed profiles
Cocktails:       209 professional recipes
Ingredients:     156 unique ingredients
Recipe Components: 847 ingredient-cocktail relationships
Lists:           45 user-created collections
Tags:            156 vibe/mood tags applied
Vessels:         12 different glass types
```

**Storage Requirements**:
- Base schema: ~2MB
- With demo data: ~15MB
- With images: ~50MB (varies by upload volume)
- Indexes: ~5MB

---

*This documentation covers the complete database architecture. For development workflows, see [development-workflow.md](development-workflow.md).*

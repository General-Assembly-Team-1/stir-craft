#!/usr/bin/env python3
"""
Import missing cocktails that have image files but no database entries.
"""
import os
import django
import requests
import time
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')
django.setup()

from stir_craft.models import Cocktail, Ingredient, Vessel, RecipeComponent, User
from django.contrib.auth.models import User as AuthUser

def get_cocktail_from_api(name):
    """Get cocktail data from TheCocktailDB API by name."""
    # Try exact name search first
    url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={name}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        drinks = data.get('drinks', [])
        if drinks:
            return drinks[0]
    except Exception as e:
        print(f"Error fetching {name}: {e}")
    
    return None

def get_or_create_admin_user():
    """Get or create admin user for imports."""
    admin_user, created = AuthUser.objects.get_or_create(
        username='cocktaildb_importer',
        defaults={
            'email': 'import@stircraft.com',
            'first_name': 'TheCocktailDB',
            'last_name': 'Importer',
            'is_active': True,
        }
    )
    return admin_user

def normalize_name(name):
    """Convert filename to potential cocktail name."""
    # Convert hyphens to spaces and title case
    return name.replace('-', ' ').title()

def import_cocktail_from_api(drink_data, admin_user):
    """Import a single cocktail from API data."""
    name = drink_data.get('strDrink')
    if not name:
        return False
    
    # Check if cocktail already exists
    if Cocktail.objects.filter(name=name).exists():
        print(f"  ✓ {name} already exists")
        return True
    
    try:
        # Create basic cocktail
        cocktail = Cocktail.objects.create(
            name=name,
            creator=admin_user,
            description=drink_data.get('strInstructions', ''),
            is_alcoholic=drink_data.get('strAlcoholic') == 'Alcoholic',
            # We'll handle image assignment later
        )
        
        # Add basic ingredients (simplified for now)
        for i in range(1, 16):  # TheCocktailDB has up to 15 ingredients
            ingredient_name = drink_data.get(f'strIngredient{i}')
            measurement = drink_data.get(f'strMeasure{i}')
            
            if ingredient_name and ingredient_name.strip():
                # Get or create ingredient
                ingredient, created = Ingredient.objects.get_or_create(
                    name=ingredient_name.strip(),
                    defaults={
                        'ingredient_type': 'other',  # Simplified for now
                        'alcohol_content': 0.0,  # Will be updated later
                    }
                )
                
                # Create recipe component
                RecipeComponent.objects.create(
                    cocktail=cocktail,
                    ingredient=ingredient,
                    amount=1.0,  # Simplified - would normally parse measurement
                    unit='oz',
                    order=i
                )
        
        print(f"  ✓ Created {name}")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to create {name}: {e}")
        return False

def main():
    print("🍸 Importing missing cocktails from TheCocktailDB...")
    
    # Get list of image files that don't have corresponding cocktails
    image_dir = Path('media/cocktails')
    if not image_dir.exists():
        print("❌ Media directory not found")
        return
    
    # Get all base image filenames (without _hash versions)
    image_files = []
    for file in image_dir.glob('*.jpg'):
        if '_' not in file.stem:  # Skip hash versions
            image_files.append(file.stem)
    
    print(f"Found {len(image_files)} unique images")
    
    # Get existing cocktail names
    existing_cocktails = set(Cocktail.objects.values_list('name', flat=True))
    print(f"Found {len(existing_cocktails)} existing cocktails")
    
    # Find missing cocktails
    missing_cocktails = []
    for image_name in image_files:
        cocktail_name = normalize_name(image_name)
        if cocktail_name not in existing_cocktails:
            missing_cocktails.append(cocktail_name)
    
    print(f"Found {len(missing_cocktails)} missing cocktails")
    
    if not missing_cocktails:
        print("✅ No missing cocktails found!")
        return
    
    # Get admin user
    admin_user = get_or_create_admin_user()
    
    # Import missing cocktails
    imported = 0
    failed = 0
    
    # Limit to first 10 for testing
    test_cocktails = missing_cocktails[:10]
    print(f"\n📡 Testing import with {len(test_cocktails)} cocktails...")
    
    for i, cocktail_name in enumerate(test_cocktails, 1):
        print(f"[{i}/{len(test_cocktails)}] Importing {cocktail_name}...")
        
        # Get cocktail data from API
        drink_data = get_cocktail_from_api(cocktail_name)
        
        if drink_data:
            if import_cocktail_from_api(drink_data, admin_user):
                imported += 1
            else:
                failed += 1
        else:
            print(f"  ✗ Not found in API: {cocktail_name}")
            failed += 1
        
        # Rate limiting
        time.sleep(0.5)
    
    print(f"\n📊 Import Summary:")
    print(f"✅ Successfully imported: {imported}")
    print(f"❌ Failed: {failed}")
    print(f"📋 Total processed: {len(test_cocktails)}")

if __name__ == '__main__':
    main()

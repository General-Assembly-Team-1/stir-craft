#!/usr/bin/env python3
import os
import django
import requests
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')
django.setup()

from stir_craft.models import Cocktail, Ingredient, Vessel, RecipeComponent, User
from django.db import transaction
from decimal import Decimal

def get_missing_cocktail_names():
    """Get list of cocktail names that have image files but no database entries."""
    # Get all base image filenames (without extension and _hash versions)
    image_dir = '/app/stircraft/media/cocktails/'
    try:
        all_files = os.listdir(image_dir)
    except:
        # For local testing
        image_dir = './media/cocktails/'
        all_files = os.listdir(image_dir) if os.path.exists(image_dir) else []
    
    base_images = set()
    for file in all_files:
        if file.endswith('.jpg') and '_' not in file:
            base_name = file.replace('.jpg', '').replace('-', ' ').title()
            base_images.add(base_name)
    
    # Get all cocktail names from database
    cocktail_names = set(Cocktail.objects.values_list('name', flat=True))
    
    # Find images without matching cocktails
    missing_cocktails = base_images - cocktail_names
    return list(missing_cocktails)

def search_cocktail_api(name):
    """Search for a cocktail by name in TheCocktailDB API."""
    print(f"  Searching API for: {name}")
    
    # Try exact name search first
    url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={name}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        drinks = data.get('drinks', [])
        if drinks:
            # Look for exact match first
            for drink in drinks:
                if drink['strDrink'].lower() == name.lower():
                    return drink
            # Return first result if no exact match
            return drinks[0]
        
        # Try searching with variations
        name_variations = [
            name.replace(' ', '-'),
            name.replace('-', ' '),
            name.replace("'", ""),
            name.replace("'s", ""),
        ]
        
        for variation in name_variations:
            if variation != name:
                url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={variation}"
                response = requests.get(url, timeout=10)
                data = response.json()
                drinks = data.get('drinks', [])
                if drinks:
                    return drinks[0]
        
        return None
        
    except Exception as e:
        print(f"    API error: {e}")
        return None

def get_or_create_admin_user():
    """Get or create admin user for imported cocktails."""
    admin_user, created = User.objects.get_or_create(
        username='cocktaildb_importer',
        defaults={
            'email': 'import@stircraft.com',
            'first_name': 'TheCocktailDB',
            'last_name': 'Importer',
            'is_active': True,
        }
    )
    return admin_user

def parse_measurement(measurement_str):
    """Parse measurement string into amount and unit."""
    if not measurement_str or measurement_str.strip() == '':
        return None, None
    
    measurement = measurement_str.strip()
    
    # Common unit mappings to valid choices
    unit_map = {
        'oz': 'oz',
        'ml': 'ml',
        'cl': 'ml',  # Convert cl to ml 
        'cup': 'oz',  # Convert cups to oz
        'cups': 'oz',
        'tsp': 'tsp',
        'tbsp': 'tbsp',
        'dash': 'dash',
        'splash': 'splash',
        'drop': 'dash',  # Convert drops to dash
        'drops': 'dash',
        'pinch': 'pinch',
        'slice': 'slice',
        'slices': 'slice',
        'part': 'oz',  # Convert parts to oz
        'parts': 'oz',
        'wedge': 'wedge',
        'sprig': 'sprig',
        'piece': 'piece',
    }
    
    # Try to extract number and unit
    import re
    
    # Pattern to match fractions, decimals, and whole numbers
    number_pattern = r'(\d+(?:\.\d+)?(?:\s*/\s*\d+)?|\d+\s*/\s*\d+)'
    match = re.search(number_pattern, measurement)
    
    if match:
        amount_str = match.group(1)
        unit_part = measurement.replace(amount_str, '').strip()
        
        # Convert fraction to decimal
        if '/' in amount_str:
            parts = amount_str.split('/')
            if len(parts) == 2:
                try:
                    amount = float(parts[0]) / float(parts[1])
                except:
                    amount = 1.0
            else:
                amount = 1.0
        else:
            try:
                amount = float(amount_str)
            except:
                amount = 1.0
        
        # Find unit
        unit = None
        for unit_key, unit_value in unit_map.items():
            if unit_key in unit_part.lower():
                unit = unit_value
                break
        
        if not unit and unit_part:
            unit = 'piece'  # Default to 'piece' if unit not recognized
        elif not unit:
            unit = 'oz'  # Default unit
        
        return Decimal(str(amount)), unit
    
    # If no number found, return default
    return Decimal('1.0'), 'piece'

def create_cocktail_from_api_data(drink_data, admin_user):
    """Create a cocktail from TheCocktailDB API data."""
    try:
        with transaction.atomic():
            # Create cocktail
            cocktail = Cocktail.objects.create(
                name=drink_data['strDrink'],
                description=drink_data.get('strInstructions', '')[:500],
                creator=admin_user,
                is_alcoholic=drink_data.get('strAlcoholic', 'Alcoholic') == 'Alcoholic',
            )
            
            # Get or create vessel
            vessel_name = drink_data.get('strGlass', 'Cocktail glass')
            vessel, _ = Vessel.objects.get_or_create(
                name=vessel_name,
                defaults={
                    'volume': Decimal('240.00'),  # Default 8 oz volume
                    'material': 'Glass',
                    'stemmed': False
                }
            )
            cocktail.vessel = vessel
            
            # Add ingredients (up to 15 possible ingredients in API)
            for i in range(1, 16):
                ingredient_key = f'strIngredient{i}'
                measure_key = f'strMeasure{i}'
                
                ingredient_name = drink_data.get(ingredient_key)
                measure = drink_data.get(measure_key)
                
                if ingredient_name and ingredient_name.strip():
                    # Get or create ingredient
                    ingredient, _ = Ingredient.objects.get_or_create(
                        name=ingredient_name.strip(),
                        defaults={
                            'description': f'{ingredient_name} ingredient',
                            'ingredient_type': 'other',
                            'alcohol_content': Decimal('0.0'),
                        }
                    )
                    
                    # Parse measurement
                    amount, unit = parse_measurement(measure)
                    
                    # Create recipe component
                    RecipeComponent.objects.create(
                        cocktail=cocktail,
                        ingredient=ingredient,
                        amount=amount or Decimal('1.0'),
                        unit=unit or 'piece',
                        preparation_note='',
                        order=i
                    )
            
            cocktail.save()
            return cocktail
            
    except Exception as e:
        print(f"    Error creating cocktail: {e}")
        return None

def main():
    print("🔍 Finding missing cocktails...")
    
    missing_cocktails = get_missing_cocktail_names()
    print(f"Found {len(missing_cocktails)} cocktails with images but no database entries")
    
    if not missing_cocktails:
        print("No missing cocktails to import!")
        return
    
    # Show sample of missing cocktails
    print("Sample missing cocktails:")
    for name in missing_cocktails[:10]:
        print(f"  - {name}")
    
    if len(missing_cocktails) > 10:
        print(f"  ... and {len(missing_cocktails) - 10} more")
    
    # Get admin user
    admin_user = get_or_create_admin_user()
    
    imported_count = 0
    not_found_count = 0
    error_count = 0
    
    print(f"\n📡 Importing missing cocktails...")
    
    for i, name in enumerate(missing_cocktails):
        print(f"[{i+1}/{len(missing_cocktails)}] {name}")
        
        # Check if already exists (in case of duplicates)
        if Cocktail.objects.filter(name__iexact=name).exists():
            print(f"  Already exists, skipping")
            continue
        
        # Search in API
        drink_data = search_cocktail_api(name)
        
        if drink_data:
            cocktail = create_cocktail_from_api_data(drink_data, admin_user)
            if cocktail:
                print(f"  ✅ Imported: {cocktail.name}")
                imported_count += 1
            else:
                print(f"  ❌ Failed to create cocktail")
                error_count += 1
        else:
            print(f"  🔍 Not found in API")
            not_found_count += 1
        
        # Rate limiting
        time.sleep(0.5)
        
        # Progress report every 10 cocktails
        if (i + 1) % 10 == 0:
            print(f"\nProgress: {i+1}/{len(missing_cocktails)} - Imported: {imported_count}, Not found: {not_found_count}, Errors: {error_count}\n")
    
    print(f"\n📊 Import Summary:")
    print(f"  Imported: {imported_count}")
    print(f"  Not found in API: {not_found_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total processed: {len(missing_cocktails)}")

if __name__ == '__main__':
    main()

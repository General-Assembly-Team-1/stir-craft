#!/usr/bin/env python
"""
Fix Cocktail Images - Update database image fields to match existing files

This script will:
1. Find all cocktail records with empty image fields
2. Look for matching image files in the media/cocktails directory
3. Update the database with the correct image paths
4. Use multiple filename patterns to find matches
"""

import os
import sys
import re
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')

import django
django.setup()

from django.conf import settings
from django.core.files import File
from stir_craft.models import Cocktail

def clean_name(name):
    """Convert cocktail name to various filename patterns"""
    # Remove special characters and convert to lowercase
    cleaned = re.sub(r'[^\w\s-]', '', name.lower())
    
    patterns = [
        # Pattern 1: Replace spaces with hyphens
        cleaned.replace(' ', '-'),
        # Pattern 2: Replace spaces with underscores  
        cleaned.replace(' ', '_'),
        # Pattern 3: Remove spaces entirely
        cleaned.replace(' ', ''),
        # Pattern 4: Replace spaces with dots
        cleaned.replace(' ', '.'),
    ]
    
    return patterns

def find_matching_image(cocktail_name, image_files):
    """Find matching image file for a cocktail name"""
    patterns = clean_name(cocktail_name)
    
    # Create a lookup dictionary for faster searching
    file_lookup = {}
    for file_path in image_files:
        base_name = file_path.stem.lower()
        file_lookup[base_name] = file_path
        
        # Also store versions without Django suffixes (e.g., "margarita_XYZ123" -> "margarita")
        if '_' in base_name:
            clean_base = base_name.split('_')[0]
            if clean_base not in file_lookup:
                file_lookup[clean_base] = file_path
    
    # Try to find a match
    for pattern in patterns:
        if pattern in file_lookup:
            return file_lookup[pattern]
    
    # Try partial matches (in case of slight differences)
    for pattern in patterns:
        for file_base in file_lookup.keys():
            if pattern in file_base or file_base in pattern:
                return file_lookup[file_base]
    
    return None

def main():
    print("🍸 StirCraft Image Fixer")
    print("=" * 50)
    
    # Get the media directory
    media_root = Path(settings.MEDIA_ROOT) if hasattr(settings, 'MEDIA_ROOT') else Path('media')
    cocktails_dir = media_root / 'cocktails'
    
    print(f"📁 Looking for images in: {cocktails_dir}")
    
    if not cocktails_dir.exists():
        print(f"❌ Cocktails directory not found: {cocktails_dir}")
        return
    
    # Get all image files
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.gif']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(cocktails_dir.glob(ext))
    
    print(f"🖼️  Found {len(image_files)} image files")
    
    # Get cocktails with empty image fields
    cocktails_without_images = Cocktail.objects.filter(
        models.Q(image='') | models.Q(image__isnull=True)
    )
    
    print(f"📋 Found {cocktails_without_images.count()} cocktails without images")
    
    if cocktails_without_images.count() == 0:
        print("✅ All cocktails already have images!")
        return
    
    updated_count = 0
    
    for cocktail in cocktails_without_images:
        print(f"\n🔍 Processing: {cocktail.name}")
        
        # Find matching image
        matching_image = find_matching_image(cocktail.name, image_files)
        
        if matching_image:
            # Calculate relative path from media root
            relative_path = matching_image.relative_to(media_root)
            
            print(f"   ✅ Found match: {matching_image.name}")
            print(f"   📎 Setting image to: {relative_path}")
            
            # Update the cocktail image field
            cocktail.image.name = str(relative_path)
            cocktail.save()
            
            updated_count += 1
        else:
            print(f"   ❌ No matching image found")
            # Show the patterns we tried
            patterns = clean_name(cocktail.name)
            print(f"   🔍 Tried patterns: {', '.join(patterns[:3])}")
    
    print(f"\n🎉 Fixed {updated_count} cocktail images!")
    
    # Show some examples of what was fixed
    if updated_count > 0:
        print("\n📊 Sample fixes:")
        fixed_cocktails = Cocktail.objects.exclude(
            models.Q(image='') | models.Q(image__isnull=True)
        )[:5]
        
        for cocktail in fixed_cocktails:
            print(f"   • {cocktail.name} → {cocktail.image.name}")

if __name__ == '__main__':
    # Import models here to avoid issues
    from django.db import models
    main()

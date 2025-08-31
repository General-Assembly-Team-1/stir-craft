#!/usr/bin/env python3
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')
django.setup()

from stir_craft.models import Cocktail

def assign_images_to_new_cocktails():
    """Assign images to cocktails that don't have them."""
    
    # Get image directory
    image_dir = '/app/stircraft/media/cocktails/'
    try:
        all_files = os.listdir(image_dir)
    except:
        # For local testing
        image_dir = './media/cocktails/'
        all_files = os.listdir(image_dir) if os.path.exists(image_dir) else []
    
    # Get base image filenames (without _hash versions)
    base_images = {}
    for file in all_files:
        if file.endswith('.jpg') and '_' not in file:
            base_name = file.replace('.jpg', '').replace('-', ' ').title()
            base_images[base_name] = file
    
    print(f"Found {len(base_images)} unique image files")
    
    # Get cocktails without images
    cocktails_without_images = Cocktail.objects.filter(image='') | Cocktail.objects.filter(image__isnull=True)
    print(f"Found {cocktails_without_images.count()} cocktails without images")
    
    matched_count = 0
    
    for cocktail in cocktails_without_images:
        # Try to find matching image
        cocktail_name_formatted = cocktail.name.replace(' ', ' ').title()
        
        # Try various name formats
        name_variations = [
            cocktail.name,
            cocktail_name_formatted,
            cocktail.name.replace('-', ' ').title(),
            cocktail.name.replace(' ', '-').title(),
            cocktail.name.lower().replace(' ', '-'),
        ]
        
        found_image = None
        for variation in name_variations:
            if variation in base_images:
                found_image = base_images[variation]
                break
        
        if found_image:
            cocktail.image = f'cocktails/{found_image}'
            cocktail.save()
            print(f"✅ Matched '{cocktail.name}' → {found_image}")
            matched_count += 1
        else:
            print(f"❌ No image found for '{cocktail.name}'")
    
    print(f"\n📊 Assignment Summary:")
    print(f"  Matched: {matched_count}")
    print(f"  Unmatched: {cocktails_without_images.count() - matched_count}")

if __name__ == '__main__':
    assign_images_to_new_cocktails()

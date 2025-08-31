#!/usr/bin/env python3
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')
django.setup()

from stir_craft.models import Cocktail

# Check for broken image links
broken_images = []
fixed_images = []

cocktails_with_images = Cocktail.objects.exclude(image='').exclude(image__isnull=True)

for cocktail in cocktails_with_images:
    image_path = cocktail.image.path if hasattr(cocktail.image, 'path') else None
    
    # For production, we need to check the actual Heroku path
    if image_path:
        # Convert to production path
        prod_path = image_path.replace('/app/stircraft', '/app/stircraft')
        
        if not os.path.exists(prod_path):
            broken_images.append({
                'name': cocktail.name,
                'image': str(cocktail.image),
                'path': prod_path
            })
        else:
            fixed_images.append({
                'name': cocktail.name,
                'image': str(cocktail.image)
            })

print(f"Cocktails with working images: {len(fixed_images)}")
print(f"Cocktails with broken images: {len(broken_images)}")

if broken_images:
    print("\nBroken images:")
    for item in broken_images[:10]:  # Show first 10
        print(f"  {item['name']} -> {item['image']}")
    
    if len(broken_images) > 10:
        print(f"  ... and {len(broken_images) - 10} more")

print(f"\nTotal cocktails checked: {len(cocktails_with_images)}")

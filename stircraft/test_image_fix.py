#!/usr/bin/env python
"""
Test script to verify the image handling fix for cocktail detail pages.
This script tests the has_image() method and demonstrates the improved logic.
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')
django.setup()

from stir_craft.models import Cocktail

def test_image_handling():
    """Test the has_image method and image URL generation."""
    print("🧪 Testing Image Handling Fix")
    print("=" * 50)
    
    # Get some cocktails to test
    cocktails = Cocktail.objects.all()[:5]
    
    if not cocktails:
        print("❌ No cocktails found in database")
        return
    
    print(f"Testing {len(cocktails)} cocktails...")
    print()
    
    for cocktail in cocktails:
        print(f"🍸 {cocktail.name}")
        print(f"   - Image field: {cocktail.image}")
        print(f"   - Has image: {cocktail.has_image()}")
        
        if cocktail.image:
            print(f"   - Image URL: {cocktail.image.url}")
            if hasattr(cocktail.image, 'path'):
                print(f"   - File exists: {os.path.exists(cocktail.image.path)}")
            else:
                print(f"   - Remote storage (no local path)")
        
        # Test the safe image URL method
        try:
            safe_url = cocktail.get_safe_image_url()
            print(f"   - Safe URL: {safe_url[:80]}{'...' if len(safe_url) > 80 else ''}")
        except Exception as e:
            print(f"   - Safe URL error: {e}")
        
        print()

if __name__ == "__main__":
    test_image_handling()

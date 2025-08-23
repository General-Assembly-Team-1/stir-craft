#!/usr/bin/env python
"""Test the cocktail create page"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')
django.setup()

from django.test import Client, override_settings
from django.contrib.auth import get_user_model

User = get_user_model()

@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_create_page():
    try:
        client = Client()
        
        # Login
        user = User.objects.get(username='testguest')
        login_result = client.login(username='testguest', password='Guest1')
        print(f"Login: {login_result}")
        
        # Access create page
        response = client.get('/cocktails/create/')
        print(f"Create page status: {response.status_code}")
        
        content = response.content.decode()
        
        # Check for key elements
        print(f"Has cocktail form: {'id=\"cocktail-form\"' in content}")
        print(f"Has add ingredient button: {'id=\"add-ingredient-btn\"' in content}")
        print(f"Has ingredient forms container: {'id=\"ingredient-forms\"' in content}")
        print(f"Has formset management: {'id=\"id_components-TOTAL_FORMS\"' in content}")
        print(f"Has cocktail-form.js: {'cocktail-form.js' in content}")
        
        # Look for formset structure
        print(f"Has ingredient rows: {'ingredient-row' in content}")
        print(f"Has Bootstrap columns: {'col-3' in content}")
        
        # Check the correct management form fields
        print(f"Has TOTAL_FORMS: {'id_components-TOTAL_FORMS' in content}")
        print(f"Has MAX_FORMS: {'id_components-MAX_NUM_FORMS' in content}")
        
        # Check if template debug is working
        if 'ingredient-row row mb-2' in content:
            print("✅ Template has been updated with Bootstrap grid structure")
        else:
            print("❌ Template still using old structure")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_page()

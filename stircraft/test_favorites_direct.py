#!/usr/bin/env python
"""Test script to test favorites functionality directly"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')
django.setup()

from django.test import Client, override_settings
from django.contrib.auth import get_user_model
from stir_craft.models import Cocktail

User = get_user_model()

@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_favorites():
    try:
        # Create client and login
        client = Client()
        
        # Get the test user
        user = User.objects.get(username='testguest')
        print(f"Found user: {user.username}")
        
        # Login
        login_result = client.login(username='testguest', password='Guest1')
        print(f"Login successful: {login_result}")
        
        # Get a cocktail
        cocktail = Cocktail.objects.first()
        print(f"Testing with cocktail: {cocktail.name} (ID: {cocktail.id})")
        
        # Test toggle favorite
        response = client.post(f'/cocktails/{cocktail.id}/favorite/', 
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        print(f"Favorite toggle response: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        
        # Test accessing cocktail detail page
        response = client.get(f'/cocktails/{cocktail.id}/')
        print(f"Detail page response: {response.status_code}")
        if response.status_code == 200 and hasattr(response, 'context') and response.context:
            print(f"User in context: {response.context.get('user')}")
            print(f"Is favorited: {response.context.get('is_favorited')}")
        else:
            print(f"No context available or error response")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_favorites()

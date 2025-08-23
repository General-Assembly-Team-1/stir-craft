#!/usr/bin/env python
"""Test login and access cocktail page directly"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')
django.setup()

from django.test import Client, override_settings
from django.contrib.auth import get_user_model

User = get_user_model()

@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_login_and_access():
    try:
        client = Client()
        
        # Login
        login_result = client.login(username='testguest', password='Guest1')
        print(f"Login result: {login_result}")
        
        # Access cocktail page while logged in
        response = client.get('/cocktails/50/')
        print(f"Cocktail page status: {response.status_code}")
        
        # Check if favorites button should be visible
        content = response.content.decode()
        
        # Look for key elements
        print(f"Contains favorite-btn: {'id=\"favorite-btn\"' in content}")
        print(f"Contains user.is_authenticated: {'user.is_authenticated' in content}")
        print(f"Contains favorites-new.js: {'favorites-new.js' in content}")
        print(f"Contains stirCraftConfig: {'stirCraftConfig' in content}")
        
        # If signed in, create a simple CURL test command
        if login_result:
            # Get session cookie for curl test
            session_cookie = None
            for cookie in client.cookies:
                if cookie.name == 'sessionid':
                    session_cookie = cookie.value
                    break
            
            if session_cookie:
                print(f"\nTo test favorites manually with curl:")
                print(f"curl -X POST http://127.0.0.1:8000/cocktails/50/favorite/ \\")
                print(f"  -H 'X-CSRFToken: <csrf_token>' \\")
                print(f"  -H 'Cookie: sessionid={session_cookie}' \\")
                print(f"  -H 'X-Requested-With: XMLHttpRequest'")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_and_access()

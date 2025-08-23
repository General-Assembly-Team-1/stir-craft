#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')
django.setup()

from django.contrib.auth.models import User
from stir_craft.models import Cocktail, List
from django.test import Client
from django.urls import reverse

# Test with our testguest user
user = User.objects.get(username='testguest')
cocktail = Cocktail.objects.first()
print(f'Testing with user: {user.username}, cocktail: {cocktail.name}')

# Check initial favorites
favorites_list = List.get_or_create_favorites_list(user)
initial_count = favorites_list.cocktails.count()
print(f'Initial favorites count: {initial_count}')

# Test the toggle_favorite endpoint directly
client = Client()
client.force_login(user)
url = reverse('toggle_favorite', args=[cocktail.id])
print(f'Testing URL: {url}')

# Make the request
response = client.post(url)
print(f'Response status: {response.status_code}')
print(f'Response content: {response.content.decode()}')

# Check if it was added to favorites
favorites_list.refresh_from_db()
new_count = favorites_list.cocktails.count()
print(f'New favorites count: {new_count}')
print(f'Success: {new_count != initial_count}')

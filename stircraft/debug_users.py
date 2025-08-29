#!/usr/bin/env python
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')

import django
django.setup()

from django.contrib.auth.models import User
from stir_craft.models import Profile

# Check users and profiles
print("=== USER AND PROFILE DEBUG ===")
print(f"Total users: {User.objects.count()}")
print(f"Total profiles: {Profile.objects.count()}")

print("\n=== ALL USERS ===")
for user in User.objects.all():
    try:
        profile = Profile.objects.get(user=user)
        print(f"User ID {user.id}: {user.username} (profile exists)")
    except Profile.DoesNotExist:
        print(f"User ID {user.id}: {user.username} (NO PROFILE)")

print("\n=== COCKTAIL CREATORS ===")
from stir_craft.models import Cocktail
creators = User.objects.filter(cocktails__isnull=False).distinct()
for creator in creators:
    cocktail_count = creator.cocktails.count()
    print(f"Creator ID {creator.id}: {creator.username} ({cocktail_count} cocktails)")

print("\n=== URL TEST ===")
# Test some URL patterns
from django.urls import reverse
try:
    # Test if user 2 exists
    if User.objects.filter(id=2).exists():
        user_2_url = reverse('profile_detail', kwargs={'user_id': 2})
        print(f"Profile URL for user 2: {user_2_url}")
    else:
        print("User ID 2 does not exist")
        
    # Show first few users
    first_users = User.objects.all()[:5]
    print("First 5 users and their profile URLs:")
    for user in first_users:
        url = reverse('profile_detail', kwargs={'user_id': user.id})
        print(f"  User {user.id} ({user.username}): {url}")
        
except Exception as e:
    print(f"Error generating URLs: {e}")

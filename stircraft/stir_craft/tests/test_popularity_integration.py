"""
Integration test script to demonstrate the popularity sorting feature.
This creates sample data and tests the sorting functionality.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TransactionTestCase
from ..models import List, Cocktail, Vessel, Ingredient, RecipeComponent


class PopularitySortingIntegrationTest(TransactionTestCase):
    """Integration test demonstrating the full popularity sorting workflow."""

    def setUp(self):
        self.client = Client()
        
        # Create users
        self.alice = User.objects.create_user(username='alice', password='pass123')
        self.bob = User.objects.create_user(username='bob', password='pass123')
        self.charlie = User.objects.create_user(username='charlie', password='pass123')
        
        # Create basic objects
        self.glass = Vessel.objects.create(name='Old Fashioned Glass', volume=300, material='Glass')
        self.whiskey = Ingredient.objects.create(
            name='Bourbon Whiskey', 
            ingredient_type='spirit', 
            alcohol_content=40.0
        )
        self.sugar = Ingredient.objects.create(
            name='Simple Syrup', 
            ingredient_type='sweetener', 
            alcohol_content=0.0
        )
        self.bitters = Ingredient.objects.create(
            name='Angostura Bitters', 
            ingredient_type='bitters', 
            alcohol_content=44.7
        )

    def test_full_popularity_sorting_workflow(self):
        """Test the complete workflow of popularity sorting from data creation to display."""
        
        # Step 1: Create cocktails with different popularity potential
        old_fashioned = Cocktail.objects.create(
            name='Old Fashioned',
            instructions='Stir with ice, strain over large ice cube',
            creator=self.alice,
            vessel=self.glass
        )
        RecipeComponent.objects.create(
            cocktail=old_fashioned, ingredient=self.whiskey, 
            amount=60.0, unit='ml', order=1
        )
        RecipeComponent.objects.create(
            cocktail=old_fashioned, ingredient=self.sugar, 
            amount=10.0, unit='ml', order=2
        )
        RecipeComponent.objects.create(
            cocktail=old_fashioned, ingredient=self.bitters, 
            amount=2.0, unit='dash', order=3
        )
        
        whiskey_sour = Cocktail.objects.create(
            name='Whiskey Sour',
            instructions='Shake with ice, strain into glass',
            creator=self.bob,
            vessel=self.glass
        )
        RecipeComponent.objects.create(
            cocktail=whiskey_sour, ingredient=self.whiskey, 
            amount=50.0, unit='ml', order=1
        )
        
        manhattan = Cocktail.objects.create(
            name='Manhattan',
            instructions='Stir with ice, strain into coupe',
            creator=self.charlie,
            vessel=self.glass
        )
        RecipeComponent.objects.create(
            cocktail=manhattan, ingredient=self.whiskey, 
            amount=60.0, unit='ml', order=1
        )
        
        # Step 2: Create favorites lists and add cocktails to simulate popularity
        # Alice likes Old Fashioned and Whiskey Sour
        alice_favorites = List.get_or_create_favorites_list(self.alice)
        alice_favorites.cocktails.add(old_fashioned, whiskey_sour)
        
        # Bob likes Old Fashioned and Manhattan  
        bob_favorites = List.get_or_create_favorites_list(self.bob)
        bob_favorites.cocktails.add(old_fashioned, manhattan)
        
        # Charlie only likes Old Fashioned
        charlie_favorites = List.get_or_create_favorites_list(self.charlie)
        charlie_favorites.cocktails.add(old_fashioned)
        
        # Expected popularity:
        # 1. Old Fashioned: 3 favorites (Alice, Bob, Charlie)
        # 2. Whiskey Sour: 1 favorite (Alice)  
        # 3. Manhattan: 1 favorite (Bob)
        
        # Step 3: Test default view (shows all cocktails)
        response = self.client.get(reverse('cocktail_index'))
        self.assertEqual(response.status_code, 200)
        
        all_cocktails = response.context['page_obj'].object_list
        self.assertEqual(len(all_cocktails), 3)
        
        # Step 4: Test popularity sorting (shows only favorited cocktails, sorted by favorites)
        response = self.client.get(reverse('cocktail_index'), {'sort_by': '-favorites_count'})
        self.assertEqual(response.status_code, 200)
        
        popular_cocktails = list(response.context['page_obj'].object_list)
        self.assertEqual(len(popular_cocktails), 3)  # All have at least 1 favorite
        
        # Verify correct ordering
        self.assertEqual(popular_cocktails[0].name, 'Old Fashioned')  # 3 favorites
        self.assertEqual(popular_cocktails[0].favorites_count, 3)
        
        # Whiskey Sour and Manhattan both have 1 favorite, should be sorted by creation date
        remaining_names = {popular_cocktails[1].name, popular_cocktails[2].name}
        self.assertEqual(remaining_names, {'Whiskey Sour', 'Manhattan'})
        
        # Step 5: Verify the form displays the new option
        self.assertContains(response, 'Most Popular (Most Favorites)')
        
        # Step 6: Test with search query + popularity sort
        response = self.client.get(reverse('cocktail_index'), {
            'sort_by': '-favorites_count',
            'query': 'Old'
        })
        self.assertEqual(response.status_code, 200)
        
        search_results = list(response.context['page_obj'].object_list)
        # Should find cocktails with "Old" in name, still sorted by popularity
        self.assertEqual(len(search_results), 1)  # Only "Old Fashioned" matches "Old"
        search_names = [c.name for c in search_results]
        self.assertIn('Old Fashioned', search_names)
        
        # Step 7: Test edge case - create cocktail with no favorites
        unpopular_cocktail = Cocktail.objects.create(
            name='Unpopular Drink',
            instructions='Nobody likes this',
            creator=self.alice,
            vessel=self.glass
        )
        
        response = self.client.get(reverse('cocktail_index'), {'sort_by': '-favorites_count'})
        popular_only = list(response.context['page_obj'].object_list)
        
        # Should not include the unpopular cocktail
        popular_names = [c.name for c in popular_only]
        self.assertNotIn('Unpopular Drink', popular_names)
        self.assertEqual(len(popular_only), 3)  # Still only the 3 favorited ones
        
        print("✅ Popularity sorting integration test passed!")
        print(f"📊 Found {len(popular_only)} popular cocktails")
        print(f"🏆 Most popular: {popular_only[0].name} ({popular_only[0].favorites_count} favorites)")

    def test_user_interaction_workflow(self):
        """Test the user interaction flow for discovering popular cocktails."""
        
        # Create a popular cocktail
        margarita = Cocktail.objects.create(
            name='Classic Margarita',
            instructions='Shake with ice, salt rim',
            creator=self.alice,
            vessel=self.glass
        )
        
        # Multiple users favorite it
        for user in [self.alice, self.bob, self.charlie]:
            favorites = List.get_or_create_favorites_list(user)
            favorites.cocktails.add(margarita)
        
        # User visits cocktail index
        response = self.client.get(reverse('cocktail_index'))
        self.assertEqual(response.status_code, 200)
        
        # User selects "Most Popular" from dropdown
        response = self.client.get(reverse('cocktail_index'), {'sort_by': '-favorites_count'})
        self.assertEqual(response.status_code, 200)
        
        # User sees popular cocktails first
        cocktails = list(response.context['page_obj'].object_list)
        self.assertEqual(cocktails[0].name, 'Classic Margarita')
        self.assertEqual(cocktails[0].favorites_count, 3)
        
        # Verify form state is preserved (check the bound form data)
        form = response.context['search_form']
        self.assertEqual(form.data.get('sort_by'), '-favorites_count')
        
        print("✅ User interaction workflow test passed!")

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import List, Cocktail, Vessel, Ingredient, RecipeComponent


class PopularitySortingTest(TestCase):
    """Tests for the new popularity-based sorting functionality."""

    def setUp(self):
        self.client = Client()
        
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.user3 = User.objects.create_user(username='user3', password='pass123')
        
        # Create test objects
        self.vessel = Vessel.objects.create(name='Test Glass', volume=200, material='Glass')
        self.ingredient = Ingredient.objects.create(
            name='Test Ingredient', 
            ingredient_type='spirit', 
            alcohol_content=40.0
        )
        
        # Create cocktails with different popularity levels
        self.cocktail_very_popular = Cocktail.objects.create(
            name='Very Popular Cocktail',
            instructions='Very popular drink',
            creator=self.user1,
            vessel=self.vessel
        )
        RecipeComponent.objects.create(
            cocktail=self.cocktail_very_popular, 
            ingredient=self.ingredient, 
            amount=50.0, 
            unit='ml', 
            order=1
        )
        
        self.cocktail_somewhat_popular = Cocktail.objects.create(
            name='Somewhat Popular Cocktail',
            instructions='Somewhat popular drink',
            creator=self.user1,
            vessel=self.vessel
        )
        RecipeComponent.objects.create(
            cocktail=self.cocktail_somewhat_popular, 
            ingredient=self.ingredient, 
            amount=60.0, 
            unit='ml', 
            order=1
        )
        
        self.cocktail_not_popular = Cocktail.objects.create(
            name='Not Popular Cocktail',
            instructions='Not favorited by anyone',
            creator=self.user1,
            vessel=self.vessel
        )
        RecipeComponent.objects.create(
            cocktail=self.cocktail_not_popular, 
            ingredient=self.ingredient, 
            amount=45.0, 
            unit='ml', 
            order=1
        )
        
        # Create favorites lists and add cocktails to create popularity hierarchy
        
        # User1 favorites (2 cocktails)
        favorites1 = List.get_or_create_favorites_list(self.user1)
        favorites1.cocktails.add(self.cocktail_very_popular, self.cocktail_somewhat_popular)
        
        # User2 favorites (2 cocktails, overlapping with user1)
        favorites2 = List.get_or_create_favorites_list(self.user2)
        favorites2.cocktails.add(self.cocktail_very_popular, self.cocktail_somewhat_popular)
        
        # User3 favorites (1 cocktail, making very_popular the most favorited)
        favorites3 = List.get_or_create_favorites_list(self.user3)
        favorites3.cocktails.add(self.cocktail_very_popular)
        
        # Expected popularity ranking:
        # 1. very_popular: 3 favorites
        # 2. somewhat_popular: 2 favorites  
        # 3. not_popular: 0 favorites (should not appear in popularity sort)

    def test_popularity_sort_shows_only_favorited_cocktails(self):
        """Test that popularity sorting only shows cocktails with at least 1 favorite."""
        url = reverse('cocktail_index')
        response = self.client.get(url, {'sort_by': '-favorites_count'})
        
        self.assertEqual(response.status_code, 200)
        
        # Get the cocktails from the response
        cocktails = response.context['page_obj'].object_list
        
        # Should only include cocktails with favorites (not the unpopular one)
        self.assertEqual(len(cocktails), 2)
        cocktail_names = [c.name for c in cocktails]
        self.assertIn('Very Popular Cocktail', cocktail_names)
        self.assertIn('Somewhat Popular Cocktail', cocktail_names)
        self.assertNotIn('Not Popular Cocktail', cocktail_names)

    def test_popularity_sort_orders_by_most_favorites(self):
        """Test that cocktails are ordered by number of favorites (most first)."""
        url = reverse('cocktail_index')
        response = self.client.get(url, {'sort_by': '-favorites_count'})
        
        self.assertEqual(response.status_code, 200)
        
        # Get the cocktails from the response
        cocktails = list(response.context['page_obj'].object_list)
        
        # Should be ordered by favorites count (descending)
        self.assertEqual(len(cocktails), 2)
        self.assertEqual(cocktails[0].name, 'Very Popular Cocktail')  # 3 favorites
        self.assertEqual(cocktails[1].name, 'Somewhat Popular Cocktail')  # 2 favorites

    def test_popularity_sort_includes_favorites_count_annotation(self):
        """Test that the popularity sort adds favorites_count annotation to cocktails."""
        url = reverse('cocktail_index')
        response = self.client.get(url, {'sort_by': '-favorites_count'})
        
        self.assertEqual(response.status_code, 200)
        
        # Get the cocktails from the response
        cocktails = list(response.context['page_obj'].object_list)
        
        # Check that favorites_count annotation is present and correct
        very_popular = next(c for c in cocktails if c.name == 'Very Popular Cocktail')
        somewhat_popular = next(c for c in cocktails if c.name == 'Somewhat Popular Cocktail')
        
        self.assertEqual(very_popular.favorites_count, 3)
        self.assertEqual(somewhat_popular.favorites_count, 2)

    def test_default_sort_shows_all_cocktails(self):
        """Test that default sorting shows all cocktails including non-favorited ones."""
        url = reverse('cocktail_index')
        response = self.client.get(url)  # No sort parameter, should use default
        
        self.assertEqual(response.status_code, 200)
        
        # Get the cocktails from the response
        cocktails = response.context['page_obj'].object_list
        
        # Should include all cocktails when not using popularity sort
        self.assertEqual(len(cocktails), 3)
        cocktail_names = [c.name for c in cocktails]
        self.assertIn('Very Popular Cocktail', cocktail_names)
        self.assertIn('Somewhat Popular Cocktail', cocktail_names)
        self.assertIn('Not Popular Cocktail', cocktail_names)

    def test_other_sort_options_still_work(self):
        """Test that other sort options continue to work normally."""
        url = reverse('cocktail_index')
        
        # Test name sorting
        response = self.client.get(url, {'sort_by': 'name'})
        self.assertEqual(response.status_code, 200)
        
        cocktails = list(response.context['page_obj'].object_list)
        self.assertEqual(len(cocktails), 3)  # Should show all cocktails
        
        # Should be alphabetically sorted
        cocktail_names = [c.name for c in cocktails]
        self.assertEqual(cocktail_names, sorted(cocktail_names))

    def test_popularity_sort_with_search_query(self):
        """Test that popularity sort works in combination with search queries."""
        url = reverse('cocktail_index')
        response = self.client.get(url, {
            'sort_by': '-favorites_count',
            'query': 'Popular'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Should filter by search query AND only show favorited cocktails
        cocktails = list(response.context['page_obj'].object_list)
        self.assertEqual(len(cocktails), 2)  # Both popular cocktails match "Popular" query
        
        # Should still be ordered by favorites
        self.assertEqual(cocktails[0].name, 'Very Popular Cocktail')
        self.assertEqual(cocktails[1].name, 'Somewhat Popular Cocktail')

    def test_popularity_sort_form_displays_correctly(self):
        """Test that the popularity sort option appears in the form."""
        url = reverse('cocktail_index')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Most Popular (Most Favorites)')

    def test_empty_result_when_no_favorites_exist(self):
        """Test behavior when no cocktails have favorites."""
        # Remove all favorites
        List.objects.filter(list_type='favorites').delete()
        
        url = reverse('cocktail_index')
        response = self.client.get(url, {'sort_by': '-favorites_count'})
        
        self.assertEqual(response.status_code, 200)
        
        # Should show no cocktails when none have favorites
        cocktails = response.context['page_obj'].object_list
        self.assertEqual(len(cocktails), 0)

    def test_popularity_sort_secondary_sort_by_date(self):
        """Test that cocktails with same favorites count are sorted by creation date."""
        # Create two more cocktails with same favorites count
        cocktail_a = Cocktail.objects.create(
            name='Cocktail A',
            instructions='First cocktail',
            creator=self.user1,
            vessel=self.vessel
        )
        RecipeComponent.objects.create(
            cocktail=cocktail_a, 
            ingredient=self.ingredient, 
            amount=50.0, 
            unit='ml', 
            order=1
        )
        
        cocktail_b = Cocktail.objects.create(
            name='Cocktail B',
            instructions='Second cocktail',
            creator=self.user1,
            vessel=self.vessel
        )
        RecipeComponent.objects.create(
            cocktail=cocktail_b, 
            ingredient=self.ingredient, 
            amount=50.0, 
            unit='ml', 
            order=1
        )
        
        # Add both to user1's favorites (same favorites count)
        favorites = List.get_or_create_favorites_list(self.user1)
        favorites.cocktails.add(cocktail_a, cocktail_b)
        
        url = reverse('cocktail_index')
        response = self.client.get(url, {'sort_by': '-favorites_count'})
        
        self.assertEqual(response.status_code, 200)
        
        # Find cocktails with 1 favorite each (should be sorted by creation date)
        cocktails = list(response.context['page_obj'].object_list)
        one_favorite_cocktails = [c for c in cocktails if getattr(c, 'favorites_count', 0) == 1]
        
        # Should be ordered by creation date (newest first) as secondary sort
        self.assertEqual(len(one_favorite_cocktails), 2)
        # Cocktail B was created after Cocktail A, so should come first
        self.assertEqual(one_favorite_cocktails[0].name, 'Cocktail B')
        self.assertEqual(one_favorite_cocktails[1].name, 'Cocktail A')

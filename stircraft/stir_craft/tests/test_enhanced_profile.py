from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import List, Cocktail, Profile, Vessel, Ingredient, RecipeComponent


class EnhancedProfileTest(TestCase):
    """Tests for enhanced profile functionality with public/private lists and stats."""

    def setUp(self):
        self.client = Client()
        
        # Create test users
        self.user1 = User.objects.create_user(username='profile_user', password='pass123')
        self.user2 = User.objects.create_user(username='other_user', password='pass123')
        
        # Create profiles (should be created automatically but let's ensure)
        self.profile1, _ = Profile.objects.get_or_create(user=self.user1)
        self.profile2, _ = Profile.objects.get_or_create(user=self.user2)
        
        # Create test objects for cocktails
        self.vessel = Vessel.objects.create(name='Test Glass', volume=200, material='Glass')
        self.ingredient = Ingredient.objects.create(
            name='Test Spirit', 
            ingredient_type='spirit', 
            alcohol_content=40.0
        )
        
        # Create cocktails for user1
        self.cocktail1 = Cocktail.objects.create(
            name='User1 Cocktail 1',
            instructions='Mix well',
            creator=self.user1,
            vessel=self.vessel
        )
        RecipeComponent.objects.create(
            cocktail=self.cocktail1, 
            ingredient=self.ingredient, 
            amount=50.0, 
            unit='ml', 
            order=1
        )
        
        self.cocktail2 = Cocktail.objects.create(
            name='User1 Cocktail 2',
            instructions='Shake with ice',
            creator=self.user1,
            vessel=self.vessel
        )
        RecipeComponent.objects.create(
            cocktail=self.cocktail2, 
            ingredient=self.ingredient, 
            amount=60.0, 
            unit='ml', 
            order=1
        )
        
        # Create cocktails for user2
        self.cocktail3 = Cocktail.objects.create(
            name='User2 Cocktail',
            instructions='Stir gently',
            creator=self.user2,
            vessel=self.vessel
        )
        RecipeComponent.objects.create(
            cocktail=self.cocktail3, 
            ingredient=self.ingredient, 
            amount=45.0, 
            unit='ml', 
            order=1
        )
        
        # Create lists for user1
        self.public_list1 = List.objects.create(
            name='Public List 1',
            description='This is a custom list',
            creator=self.user1,
            list_type='custom'
        )
        self.public_list1.cocktails.add(self.cocktail1)
        
        self.private_list1 = List.objects.create(
            name='Private List 1',
            description='This is another custom list',
            creator=self.user1,
            list_type='custom'
        )
        self.private_list1.cocktails.add(self.cocktail2)
        
        # Use the get_or_create method instead of manual creation
        self.favorites_list1 = List.get_or_create_favorites_list(self.user1)
        
        # Create lists for user2
        self.public_list2 = List.objects.create(
            name='Public List 2',
            description='Another custom list',
            creator=self.user2,
            list_type='custom'
        )
        self.public_list2.cocktails.add(self.cocktail3)
        
        self.private_list2 = List.objects.create(
            name='Private List 2',
            description='Another custom list',
            creator=self.user2,
            list_type='custom'
        )

    def test_own_profile_view_authenticated(self):
        """Test viewing own profile when authenticated shows all lists and stats."""
        self.client.login(username='profile_user', password='pass123')
        url = reverse('profile_detail')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check context data
        self.assertEqual(response.context['user'], self.user1)
        self.assertEqual(response.context['profile'], self.profile1)
        self.assertEqual(response.context['stats']['cocktails_created'], 2)  # user1 created 2 cocktails
        
        # Should see all own lists (including private and special types)
        public_lists = response.context['public_lists']
        self.assertEqual(len(public_lists), 4)  # public, private, favorites, your creations
        list_names = [lst.name for lst in public_lists]
        self.assertIn('Public List 1', list_names)
        self.assertIn('Private List 1', list_names)
        self.assertIn('Favorites', list_names)
        self.assertIn('Your Creations', list_names)

    def test_own_profile_view_unauthenticated(self):
        """Test accessing own profile URL without authentication redirects to login."""
        url = reverse('profile_detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/sign-in/', response.url)

    def test_other_user_profile_view_authenticated(self):
        """Test viewing another user's profile shows only custom lists (not favorites/creations)."""
        self.client.login(username='profile_user', password='pass123')
        url = reverse('profile_detail', kwargs={'user_id': self.user2.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check context data
        self.assertEqual(response.context['user'], self.user2)
        self.assertEqual(response.context['profile'], self.profile2)
        self.assertEqual(response.context['stats']['cocktails_created'], 1)  # user2 created 1 cocktail
        
        # Should only see custom lists (excluding favorites/creations)
        public_lists = response.context['public_lists']
        self.assertEqual(len(public_lists), 2)  # Only custom lists
        list_names = [lst.name for lst in public_lists]
        self.assertIn('Public List 2', list_names)
        self.assertIn('Private List 2', list_names)
        
        # Check that all returned lists are custom type
        for lst in public_lists:
            self.assertEqual(lst.list_type, 'custom')

    def test_other_user_profile_view_unauthenticated(self):
        """Test viewing another user's profile when not authenticated shows only custom lists."""
        url = reverse('profile_detail', kwargs={'user_id': self.user2.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check context data
        self.assertEqual(response.context['user'], self.user2)
        self.assertEqual(response.context['profile'], self.profile2)
        self.assertEqual(response.context['stats']['cocktails_created'], 1)
        
        # Should only see custom lists
        public_lists = response.context['public_lists']
        self.assertEqual(len(public_lists), 2)  # Only custom lists
        for lst in public_lists:
            self.assertEqual(lst.list_type, 'custom')

    def test_profile_stats_calculation(self):
        """Test that profile stats are calculated correctly."""
        self.client.login(username='profile_user', password='pass123')
        url = reverse('profile_detail')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check cocktails created count
        self.assertEqual(response.context['stats']['cocktails_created'], 2)
        
        # Check public lists count in stats
        self.assertEqual(response.context['stats']['public_lists'], 4)  # All lists for own profile (public, private, favorites, creations)

    def test_profile_nonexistent_user(self):
        """Test viewing profile of non-existent user returns 404."""
        self.client.login(username='profile_user', password='pass123')
        url = reverse('profile_detail', kwargs={'user_id': 9999})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_profile_lists_exclude_system_types_for_others(self):
        """Test that viewing others' profiles excludes system list types like favorites/creations."""
        # Use the get_or_create method for creations list
        creations_list = List.get_or_create_creations_list(self.user2)
        
        self.client.login(username='profile_user', password='pass123')
        url = reverse('profile_detail', kwargs={'user_id': self.user2.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Should only see custom lists, not system lists
        public_lists = response.context['public_lists']
        list_types = [lst.list_type for lst in public_lists]
        self.assertNotIn('creations', list_types)
        self.assertNotIn('favorites', list_types)
        
        # Should only contain custom type lists
        for lst in public_lists:
            self.assertEqual(lst.list_type, 'custom')

    def test_profile_template_context_variables(self):
        """Test that all required template context variables are present."""
        self.client.login(username='profile_user', password='pass123')
        url = reverse('profile_detail')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check all expected context variables
        expected_vars = ['user', 'profile', 'public_lists', 'stats']
        for var in expected_vars:
            self.assertIn(var, response.context)
        
        # Check that user is viewing own profile
        self.assertEqual(response.context['user'], self.user1)
        
        # Test for other user
        url = reverse('profile_detail', kwargs={'user_id': self.user2.id})
        response = self.client.get(url)
        self.assertEqual(response.context['user'], self.user2)

    def test_profile_template_rendering(self):
        """Test that profile template renders without errors."""
        self.client.login(username='profile_user', password='pass123')
        url = reverse('profile_detail')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.username)
        self.assertContains(response, 'Public List 1')
        self.assertContains(response, 'Private List 1')
        
        # Test other user profile
        url = reverse('profile_detail', kwargs={'user_id': self.user2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user2.username)
        self.assertContains(response, 'Public List 2')
        self.assertContains(response, 'Private List 2')  # Both custom lists should show

    def test_profile_empty_lists_handling(self):
        """Test profile view handles users with no lists gracefully."""
        # Create a user with no lists
        empty_user = User.objects.create_user(username='empty_user', password='pass123')
        empty_profile, _ = Profile.objects.get_or_create(user=empty_user)
        
        self.client.login(username='profile_user', password='pass123')
        url = reverse('profile_detail', kwargs={'user_id': empty_user.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['public_lists']), 0)
        self.assertEqual(response.context['stats']['cocktails_created'], 0)

    def test_profile_list_cocktail_counts(self):
        """Test that list cocktail counts are accurate in profile view."""
        self.client.login(username='profile_user', password='pass123')
        url = reverse('profile_detail')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check that lists show correct cocktail counts
        public_lists = response.context['public_lists']
        for lst in public_lists:
            if lst.name == 'Public List 1':
                self.assertEqual(lst.cocktail_count(), 1)
            elif lst.name == 'Private List 1':
                self.assertEqual(lst.cocktail_count(), 1)
            elif lst.name == 'Favorites':
                self.assertEqual(lst.cocktail_count(), 0)

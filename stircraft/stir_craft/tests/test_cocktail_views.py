from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client
from ..models import Ingredient, Cocktail, RecipeComponent, Vessel
from datetime import date


class CocktailViewTest(TestCase):
    """
    Test class for cocktail-related views.
    
    Tests the HTTP endpoints and user interactions for cocktail management.
    """
    
    def setUp(self):
        """Set up test data for view tests."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='cocktail_user',
            email='user@stircraft.com',
            password='test_password_123'
        )
        self.vessel = Vessel.objects.create(
            name='Old Fashioned Glass',
            volume=200.0,
            material='Glass'
        )
        self.vodka = Ingredient.objects.create(
            name='Premium Vodka',
            ingredient_type='spirit',
            alcohol_content=40.0
        )
        self.juice = Ingredient.objects.create(
            name='Cranberry Juice',
            ingredient_type='juice',
            alcohol_content=0.0
        )

    def test_cocktail_index_view(self):
        """Test cocktail index view displays correctly."""
        # Create a test cocktail
        cocktail = Cocktail.objects.create(
            name='Test Cocktail',
            instructions='Mix and serve',
            creator=self.user
        )
        
        response = self.client.get(reverse('cocktail_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, cocktail.name)
        self.assertContains(response, 'Browse Cocktails')

    def test_cocktail_detail_view(self):
        """Test cocktail detail view shows complete recipe."""
        cocktail = Cocktail.objects.create(
            name='Detailed Cocktail',
            description='A test cocktail with details',
            instructions='Detailed mixing instructions',
            creator=self.user,
            vessel=self.vessel
        )
        
        # Add ingredients
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.vodka,
            amount=50.0,
            unit='ml',
            preparation_note='Chilled'
        )
        
        response = self.client.get(reverse('cocktail_detail', args=[cocktail.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, cocktail.name)
        self.assertContains(response, cocktail.description)
        self.assertContains(response, self.vodka.name)
        self.assertContains(response, 'Chilled')

    def test_cocktail_create_view_get(self):
        """Test cocktail create view shows form (GET request)."""
        self.client.login(username='cocktail_user', password='test_password_123')
        response = self.client.get(reverse('cocktail_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Cocktail')
        self.assertContains(response, 'cocktail-form')  # Template uses ID with hyphen
        self.assertContains(response, 'formset')

    def test_cocktail_create_view_post_valid(self):
        """Test cocktail creation with valid data."""
        self.client.login(username='cocktail_user', password='test_password_123')
        
        post_data = {
            # Main cocktail form data
            'name': 'Test Creation',
            'instructions': 'Mix ingredients well',
            'vessel': self.vessel.id,
            'is_alcoholic': True,
            
            # Formset management data
            'components-TOTAL_FORMS': '2',
            'components-INITIAL_FORMS': '0',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
            
            # First ingredient
            'components-0-ingredient': self.vodka.id,
            'components-0-amount': '50',
            'components-0-unit': 'ml',
            'components-0-order': '1',
            
            # Second ingredient
            'components-1-ingredient': self.juice.id,
            'components-1-amount': '100',
            'components-1-unit': 'ml',
            'components-1-order': '2',
        }
        
        response = self.client.post(reverse('cocktail_create'), data=post_data)
        
        # Should redirect to detail view on success
        self.assertEqual(response.status_code, 302)
        
        # Check that cocktail was created
        cocktail = Cocktail.objects.get(name='Test Creation')
        self.assertEqual(cocktail.creator, self.user)
        self.assertEqual(cocktail.components.count(), 2)

    def test_cocktail_create_view_post_invalid(self):
        """Test cocktail creation with invalid data shows errors."""
        self.client.login(username='cocktail_user', password='test_password_123')
        
        post_data = {
            # Missing required name and instructions
            'vessel': self.vessel.id,
            
            # Empty formset (violates min_num=1)
            'components-TOTAL_FORMS': '0',
            'components-INITIAL_FORMS': '0',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
        }
        
        response = self.client.post(reverse('cocktail_create'), data=post_data)
        self.assertEqual(response.status_code, 200)  # Stay on form page
        self.assertContains(response, 'Please correct the errors below')

    def test_cocktail_create_requires_login(self):
        """Test that cocktail creation requires authentication."""
        response = self.client.get(reverse('cocktail_create'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_cocktail_index_search_functionality(self):
        """Test search functionality in cocktail index view."""
        # Create test cocktails
        cocktail1 = Cocktail.objects.create(
            name='Bloody Mary',
            instructions='Mix with tomato juice',
            creator=self.user
        )
        cocktail2 = Cocktail.objects.create(
            name='Margarita',
            instructions='Mix with lime juice',
            creator=self.user
        )
        
        # Search for specific cocktail
        response = self.client.get(reverse('cocktail_index'), {'query': 'mary'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bloody Mary')
        self.assertNotContains(response, 'Margarita')

    def test_cocktail_index_filter_by_ingredient(self):
        """Test filtering cocktails by ingredient."""
        cocktail = Cocktail.objects.create(
            name='Vodka Cocktail',
            instructions='Mix with vodka',
            creator=self.user
        )
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.vodka,
            amount=50.0,
            unit='ml'
        )
        
        response = self.client.get(reverse('cocktail_index'), {'ingredient': self.vodka.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vodka Cocktail')

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
        self.client.login(username='cocktail_user', password='test_password_123')
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
        self.assertIn('/sign-in/', response.url)

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

    def test_cocktail_index_filter_by_spirit(self):
        """Test filtering cocktails by spirit."""
        # Create a spirit ingredient
        rum = Ingredient.objects.create(
            name='Dark Rum',
            ingredient_type='spirit',
            alcohol_content=40.0
        )
        
        cocktail = Cocktail.objects.create(
            name='Rum Cocktail',
            instructions='Mix with rum',
            creator=self.user
        )
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=rum,
            amount=50.0,
            unit='ml'
        )
        
        response = self.client.get(reverse('cocktail_index'), {'spirit': rum.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rum Cocktail')

    def test_cocktail_update_happy_path(self):
        """Creator can update cocktail and components."""
        self.client.login(username='cocktail_user', password='test_password_123')
        cocktail = Cocktail.objects.create(
            name='Update Me',
            instructions='Old instructions',
            creator=self.user,
            vessel=self.vessel
        )

        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.juice,
            amount=30.0,
            unit='ml'
        )

        post_data = {
            'name': 'Updated Cocktail',
            'instructions': 'New instructions',
            'vessel': self.vessel.id,

            # Management form - crucial for formsets
            'components-TOTAL_FORMS': '1',
            'components-INITIAL_FORMS': '1', 
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',

            # Update existing component
            'components-0-id': str(cocktail.components.first().id),
            'components-0-ingredient': self.juice.id,
            'components-0-amount': '45',
            'components-0-unit': 'ml',
            'components-0-order': '1',
            'components-0-DELETE': '',  # Required for can_delete=True formsets
        }

        response = self.client.post(reverse('cocktail_update', args=[cocktail.id]), data=post_data)
        self.assertEqual(response.status_code, 302)
        cocktail.refresh_from_db()
        self.assertEqual(cocktail.name, 'Updated Cocktail')
        self.assertEqual(cocktail.components.first().amount, 45)

    def test_cocktail_update_invalid_form_shows_errors(self):
        """Invalid update (e.g., remove all components) should show errors."""
        self.client.login(username='cocktail_user', password='test_password_123')
        cocktail = Cocktail.objects.create(
            name='Bad Update',
            instructions='Keep me',
            creator=self.user,
            vessel=self.vessel
        )

        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.vodka,
            amount=10.0,
            unit='ml'
        )

        post_data = {
            'name': '',  # remove required name
            'instructions': '',
            'vessel': self.vessel.id,

            'components-TOTAL_FORMS': '0',
            'components-INITIAL_FORMS': '1',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
        }

        response = self.client.post(reverse('cocktail_update', args=[cocktail.id]), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the errors below')

    def test_cocktail_update_permission_denied_for_non_creator(self):
        """Only creator may edit a cocktail."""
        other = User.objects.create_user(username='other', password='pass')
        cocktail = Cocktail.objects.create(
            name='Locked',
            instructions='None',
            creator=self.user,
        )

        self.client.login(username='other', password='pass')
        response = self.client.get(reverse('cocktail_update', args=[cocktail.id]))
        self.assertEqual(response.status_code, 403)

    def test_cocktail_delete_restricted_to_staff(self):
        """Creators are anonymized on delete; staff may fully delete."""
        cocktail = Cocktail.objects.create(
            name='ToDelete',
            instructions='Delete me',
            creator=self.user,
        )

        # Non-staff creator should anonymize the cocktail instead of full deletion
        self.client.login(username='cocktail_user', password='test_password_123')
        response = self.client.post(reverse('cocktail_delete', args=[cocktail.id]))
        # After anonymize, redirect to detail page
        self.assertEqual(response.status_code, 302)
        cocktail.refresh_from_db()
        self.assertNotEqual(cocktail.creator, self.user)
        self.assertEqual(cocktail.creator.username, 'anonymous')

        # Ensure the original user's creations list no longer includes the cocktail
        creations_list = cocktail.creator.created_lists.filter(list_type='creations').first()
        # The creations list belongs to the anonymous user now; check original user's creations
        orig_creations = self.user.created_lists.filter(list_type='creations').first()
        if orig_creations:
            self.assertFalse(orig_creations.cocktails.filter(id=cocktail.id).exists())

        # Create another cocktail to test staff full-delete
        cocktail2 = Cocktail.objects.create(
            name='StaffDelete',
            instructions='Delete me fully',
            creator=self.user,
        )
        # Make staff user and try full deletion
        self.user.is_staff = True
        self.user.save()
        response = self.client.post(reverse('cocktail_delete', args=[cocktail2.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Cocktail.objects.filter(name='StaffDelete').exists())

    def test_ingredient_create_requires_login(self):
        """Test that ingredient creation requires authentication"""
        self.client.logout()
        response = self.client.post(reverse('ingredient_add'), {
            'name': 'Test Ingredient',
            'category': 'spirit',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_ingredient_create_functionality(self):
        """Test the core functionality of ingredient creation"""
        self.client.login(username='cocktail_user', password='test_password_123')
        
        # Debug: Check login status
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200, "User should be logged in")
        
        # First test: Check that we can access the form
        response = self.client.get(reverse('ingredient_add'))
        if response.status_code == 302:
            # Follow the redirect to see where it goes
            response = self.client.get(reverse('ingredient_add'), follow=True)
            self.assertEqual(response.status_code, 200, f"Should be able to access ingredient form, redirected to: {response.redirect_chain}")
        else:
            self.assertEqual(response.status_code, 200)
        
        # Test successful ingredient creation via standard form submission
        initial_count = Ingredient.objects.count()
        response = self.client.post(reverse('ingredient_add'), {
            'name': 'New Test Ingredient',
            'ingredient_type': 'spirit',
            'alcohol_content': '40.0',
            'flavor_tags': 'sweet, fruity',
        }, follow=True)  # Follow redirects
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        
        # Check that ingredient was created
        new_count = Ingredient.objects.count()
        self.assertEqual(new_count, initial_count + 1)
        
        # Verify the ingredient exists and has correct properties
        ingredient = Ingredient.objects.get(name='New Test Ingredient')
        self.assertEqual(ingredient.ingredient_type, 'spirit')
        flavor_names = [tag.name for tag in ingredient.flavor_tags.all()]
        self.assertIn('sweet', flavor_names)
        self.assertIn('fruity', flavor_names)

    def test_ingredient_duplicate_prevention(self):
        """Test that duplicate ingredients are prevented"""
        self.client.login(username='cocktail_user', password='test_password_123')
        
        # Try to create duplicate ingredient (Vodka already exists)
        initial_count = Ingredient.objects.filter(name__iexact='Vodka').count()
        
        response = self.client.post(reverse('ingredient_add'), {
            'name': 'Vodka',  # Already exists
            'category': 'spirit',
        })
        
        # Should not create a duplicate
        final_count = Ingredient.objects.filter(name__iexact='Vodka').count()
        self.assertEqual(final_count, initial_count)  # No new ingredients
        
        # Test case-insensitive duplicate
        response = self.client.post(reverse('ingredient_add'), {
            'name': 'VODKA',  # Different case
            'category': 'spirit',
        })
        
        # Still should not create a duplicate
        final_count = Ingredient.objects.filter(name__iexact='VODKA').count()
        self.assertEqual(final_count, initial_count)  # Still no new ingredients

    def test_ingredient_create_duplicate_handling(self):
        """Test that duplicate ingredient creation returns helpful error"""
        self.client.login(username='cocktail_user', password='test_password_123')
        
        # Try to create duplicate ingredient
        response = self.client.post(reverse('ingredient_add'), {
            'name': 'Premium Vodka',  # Already exists in setUp
            'ingredient_type': 'spirit',
            'alcohol_content': '40',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('errors', data)
        self.assertIn('name', data['errors'])
        error_message = data['errors']['name'][0]
        self.assertIn('already exists', error_message)
        self.assertIn('Spirit', error_message)  # Should mention category (title case)

    def test_ingredient_create_case_insensitive_duplicate(self):
        """Test that case-insensitive duplicates are detected"""
        self.client.login(username='cocktail_user', password='test_password_123')
        
        response = self.client.post(reverse('ingredient_add'), {
            'name': 'premium vodka',  # Case-insensitive test with existing "Premium Vodka"
            'ingredient_type': 'spirit',
            'alcohol_content': '40',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('already exists', data['errors']['name'][0])

    def test_ingredient_create_non_ajax_request(self):
        """Test that non-AJAX requests are handled properly"""
        self.client.login(username='cocktail_user', password='test_password_123')
        
        response = self.client.post(reverse('ingredient_add'), {
            'name': 'Test Ingredient',
            'category': 'spirit',
        })
        
        # Should redirect or return appropriate response for non-AJAX
        self.assertIn(response.status_code, [200, 302])

    def test_ingredient_create_invalid_data(self):
        """Test ingredient creation with invalid data"""
        self.client.login(username='cocktail_user', password='test_password_123')
        
        response = self.client.post(reverse('ingredient_add'), {
            'name': '',  # Empty name
            'category': 'invalid_category',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('errors', data)

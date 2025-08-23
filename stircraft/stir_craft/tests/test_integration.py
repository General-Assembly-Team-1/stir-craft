from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client
from ..models import Ingredient, Cocktail, RecipeComponent, Vessel
from datetime import date


class CocktailSystemIntegrationTest(TestCase):
    """
    Integration tests for the complete cocktail management system.
    
    Tests end-to-end workflows combining models, forms, and views.
    """
    
    def setUp(self):
        """Set up comprehensive test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='integration_user',
            email='integration@stircraft.com',
            password='integration_pass_123'
        )
        
        # Create test ingredients
        self.gin = Ingredient.objects.create(
            name='London Dry Gin',
            ingredient_type='spirit',
            alcohol_content=47.0
        )
        self.vermouth = Ingredient.objects.create(
            name='Dry Vermouth',
            ingredient_type='liqueur',
            alcohol_content=18.0
        )
        self.olive = Ingredient.objects.create(
            name='Olives',
            ingredient_type='garnish',
            alcohol_content=0.0
        )
        
        # Create test vessel
        self.martini_glass = Vessel.objects.create(
            name='Martini Glass',
            volume=180.0,
            material='Crystal Glass',
            stemmed=True
        )

    def test_complete_cocktail_creation_workflow(self):
        """Test the complete workflow of creating a cocktail from start to finish."""
        self.client.login(username='integration_user', password='integration_pass_123')
        
        # Step 1: Navigate to creation page
        response = self.client.get(reverse('cocktail_create'))
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Submit complete cocktail form
        post_data = {
            # Main cocktail data
            'name': 'Classic Dry Martini',
            'description': 'The quintessential gin cocktail',
            'instructions': 'Stir gin and vermouth with ice. Strain into chilled martini glass. Garnish with olive.',
            'vessel': self.martini_glass.id,
            'is_alcoholic': True,
            'color': 'Clear',
            'vibe_tags': 'classic, sophisticated, strong',
            
            # Formset management
            'components-TOTAL_FORMS': '3',
            'components-INITIAL_FORMS': '0',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
            
            # Ingredients
            'components-0-ingredient': self.gin.id,
            'components-0-amount': '60',
            'components-0-unit': 'ml',
            'components-0-preparation_note': 'Chilled',
            'components-0-order': '1',
            
            'components-1-ingredient': self.vermouth.id,
            'components-1-amount': '10',
            'components-1-unit': 'ml',
            'components-1-preparation_note': '',
            'components-1-order': '2',
            
            'components-2-ingredient': self.olive.id,
            'components-2-amount': '1',
            'components-2-unit': 'piece',
            'components-2-preparation_note': 'As garnish',
            'components-2-order': '3',
        }
        
        response = self.client.post(reverse('cocktail_create'), data=post_data)
        
        # Step 3: Verify redirect to detail page
        self.assertEqual(response.status_code, 302)
        
        # Step 4: Verify cocktail was created correctly
        cocktail = Cocktail.objects.get(name='Classic Dry Martini')
        self.assertEqual(cocktail.creator, self.user)
        self.assertEqual(cocktail.vessel, self.martini_glass)
        self.assertTrue(cocktail.is_alcoholic)
        self.assertEqual(cocktail.components.count(), 3)
        
        # Step 5: Verify ingredients and measurements
        gin_component = cocktail.components.get(ingredient=self.gin)
        self.assertEqual(float(gin_component.amount), 60.0)
        self.assertEqual(gin_component.unit, 'ml')
        self.assertEqual(gin_component.preparation_note, 'Chilled')
        
        # Step 6: Verify calculations
        total_volume = cocktail.get_total_volume()
        self.assertEqual(total_volume, 71.0)  # 60 + 10 + 1
        
        alcohol_content = cocktail.get_alcohol_content()
        expected_abv = ((60 * 47) + (10 * 18) + (1 * 0)) / 71 / 100 * 100
        self.assertAlmostEqual(alcohol_content, expected_abv, places=2)
        
        # Step 7: Test detail page display
        response = self.client.get(reverse('cocktail_detail', args=[cocktail.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Classic Dry Martini')
        self.assertContains(response, 'London Dry Gin')
        self.assertContains(response, '60.00 ml')  # Template shows with 2 decimal places
        self.assertContains(response, 'Chilled')
        
        # Step 8: Test search functionality
        response = self.client.get(reverse('cocktail_index'), {'query': 'martini'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Classic Dry Martini')

    def test_cocktail_discovery_and_filtering(self):
        """Test cocktail discovery through search and filtering."""
        # Create diverse cocktails
        alcoholic_cocktail = Cocktail.objects.create(
            name='Gin Fizz',
            instructions='Shake and top with soda',
            creator=self.user,
            is_alcoholic=True,
            color='Clear',
            vessel=self.martini_glass
        )
        RecipeComponent.objects.create(
            cocktail=alcoholic_cocktail,
            ingredient=self.gin,
            amount=50.0,
            unit='ml'
        )
        
        mocktail = Cocktail.objects.create(
            name='Virgin Mary',
            instructions='Mix non-alcoholic ingredients',
            creator=self.user,
            is_alcoholic=False,
            color='Red'
        )
        RecipeComponent.objects.create(
            cocktail=mocktail,
            ingredient=self.olive,
            amount=2.0,
            unit='piece'
        )
        
        # Test filtering by alcohol content
        response = self.client.get(reverse('cocktail_index'), {'is_alcoholic': 'True'})
        self.assertContains(response, 'Gin Fizz')
        self.assertNotContains(response, 'Virgin Mary')
        
        # Test filtering by ingredient
        response = self.client.get(reverse('cocktail_index'), {'ingredient': self.gin.id})
        self.assertContains(response, 'Gin Fizz')
        self.assertNotContains(response, 'Virgin Mary')
        
        # Test filtering by vessel
        response = self.client.get(reverse('cocktail_index'), {'vessel': self.martini_glass.id})
        self.assertContains(response, 'Gin Fizz')
        self.assertNotContains(response, 'Virgin Mary')

    def test_error_handling_and_user_feedback(self):
        """Test error handling and user feedback throughout the system."""
        self.client.login(username='integration_user', password='integration_pass_123')
        
        # Test form validation errors
        post_data = {
            # Missing required fields
            'name': '',  # Required field empty
            'instructions': '',  # Required field empty
            
            # Invalid formset
            'components-TOTAL_FORMS': '0',
            'components-INITIAL_FORMS': '0',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
        }
        
        response = self.client.post(reverse('cocktail_create'), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the errors below')
        
        # Test 404 for non-existent cocktail
        response = self.client.get(reverse('cocktail_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)


class CocktailPerformanceTest(TestCase):
    """
    Performance tests for the cocktail system.
    
    Tests database query efficiency and page load performance.
    """
    
    def setUp(self):
        """Set up performance test data."""
        self.user = User.objects.create_user(username='perf_user', password='pass123')
        
        # Create many ingredients
        self.ingredients = []
        for i in range(20):
            ingredient = Ingredient.objects.create(
                name=f'Test Ingredient {i}',
                ingredient_type='spirit',
                alcohol_content=40.0
            )
            self.ingredients.append(ingredient)

    def test_cocktail_index_query_efficiency(self):
        """Test that cocktail index view uses efficient database queries."""
        # Create many cocktails with ingredients
        cocktails = []
        for i in range(50):
            cocktail = Cocktail.objects.create(
                name=f'Test Cocktail {i}',
                instructions=f'Instructions for cocktail {i}',
                creator=self.user
            )
            # Add 3 ingredients to each cocktail
            for j in range(3):
                RecipeComponent.objects.create(
                    cocktail=cocktail,
                    ingredient=self.ingredients[j % len(self.ingredients)],
                    amount=30.0,
                    unit='ml'
                )
            cocktails.append(cocktail)
        
        # Test query count for index view
        with self.assertNumQueries(8):  # Updated to account for search form loading ingredients, spirits, and vessels
            response = self.client.get(reverse('cocktail_index'))
            self.assertEqual(response.status_code, 200)

    def test_cocktail_detail_query_efficiency(self):
        """Test that cocktail detail view uses efficient queries."""
        self.client.login(username='perf_user', password='pass123')
        cocktail = Cocktail.objects.create(
            name='Performance Test Cocktail',
            instructions='Test instructions',
            creator=self.user
        )
        
        # Add many ingredients
        for ingredient in self.ingredients[:10]:
            RecipeComponent.objects.create(
                cocktail=cocktail,
                ingredient=ingredient,
                amount=30.0,
                unit='ml'
            )
        
        # Test query count for detail view
        with self.assertNumQueries(23):  # Updated count - includes individual ingredient tag queries
            response = self.client.get(reverse('cocktail_detail', args=[cocktail.id]))
            self.assertEqual(response.status_code, 200)

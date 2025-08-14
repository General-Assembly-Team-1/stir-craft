from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse
from django.test import Client
from .models import Profile, Ingredient, Cocktail, RecipeComponent, Vessel, List
from .forms.cocktail_forms import CocktailForm, RecipeComponentForm, RecipeComponentFormSet, CocktailSearchForm
from datetime import date

# =============================================================================
# 🧪 STIR CRAFT MODEL TESTING FRAMEWORK
# =============================================================================
# 
# This file contains automated tests to validate our cocktail/mocktail app models,
# forms, and views. Django's testing framework creates a temporary database for 
# each test run, so we can safely create, modify, and delete test data without 
# affecting our production database.
#
# HOW TO RUN TESTS:
# - Run all tests: python manage.py test
# - Run specific app tests: python manage.py test stir_craft
# - Run specific test class: python manage.py test stir_craft.tests.CocktailFormTest
# - Run with verbose output: python manage.py test --verbosity=2
#
# TEST CATEGORIES:
# - Model Tests: Validate model creation, validation, and methods
# - Form Tests: Test form validation and data processing
# - View Tests: Test HTTP requests, responses, and user interactions
# - Integration Tests: Test complete workflows and interactions
# =============================================================================


class BaseModelTest(TestCase):
    """
    STEP 1: Base test class with common setup for all model tests.
    
    This class provides shared functionality that other test classes can inherit.
    Using setUpTestData() instead of setUp() for better performance - it runs
    once per test class instead of once per test method.
    """
    
    @classmethod
    def setUpTestData(cls):
        """
        STEP 2: Create test data that will be used across multiple test methods.
        
        This method runs once when the test class is loaded, creating objects
        that can be referenced in all test methods within this class.
        """
        # Create a test user for recipes that require user ownership
        cls.test_user = User.objects.create_user(
            username='bartender_test',
            email='test@stircraft.com',
            password='test_password_123'
        )
        
        # Add more common test objects here as models are created
        # Example: cls.test_category = DrinkCategory.objects.create(name="Cocktail")


class IngredientModelTest(BaseModelTest):
    """
    STEP 3: Test class for Ingredient model functionality.
    
    Each method starting with 'test_' will be run as a separate test case.
    Tests should be focused on one specific behavior or requirement.
    """
    
    def test_ingredient_creation(self):
        """
        Test that an Ingredient can be created with valid fields.
        """
        ingredient = Ingredient.objects.create(
            name="Lime Juice",
            ingredient_type="juice",
            alcohol_content=0.0,  # Non-alcoholic
            description="Fresh lime juice for cocktails and mocktails"
        )
        self.assertEqual(ingredient.name, "Lime Juice")
        self.assertEqual(ingredient.ingredient_type, "juice")
        self.assertEqual(str(ingredient), "Lime Juice")  # Tests __str__ method
        self.assertFalse(ingredient.is_alcoholic())  # Tests custom method

    def test_ingredient_validation(self):
        """
        Test model validation and constraints.
        
        This test will verify that the model enforces business rules like:
        - Required fields cannot be empty
        - Alcohol content is within valid range (0-100%)
        - Name uniqueness if required
        """
        with self.assertRaises(ValidationError):
            invalid_ingredient = Ingredient(name="", ingredient_type="invalid")
            invalid_ingredient.full_clean()  # Triggers model validation
        
        self.assertTrue(True, "Ingredient validation tests ready for implementation")


class VesselModelTest(BaseModelTest):
    """
    Test class for Vessel model functionality.
    """

    def test_vessel_creation(self):
        """
        Test that a Vessel can be created with valid fields.
        """
        vessel = Vessel.objects.create(
            name="Highball Glass",
            volume=300.0,  # Capacity in milliliters
            material="Glass",
            stemmed=False
        )
        self.assertEqual(vessel.name, "Highball Glass")
        self.assertEqual(vessel.volume, 300.0)
        self.assertEqual(vessel.material, "Glass")
        self.assertFalse(vessel.stemmed)
        self.assertEqual(str(vessel), "Highball Glass")

    def test_vessel_validation(self):
        """
        Test model validation and constraints.
        """
        with self.assertRaises(ValidationError):
            invalid_vessel = Vessel(name="", volume=-100.0, material="Glass", stemmed=False)
            invalid_vessel.full_clean()  # Triggers model validation

        self.assertTrue(True, "Vessel validation tests ready for implementation")


class CocktailModelTest(BaseModelTest):
    """
    Test class for Cocktail model functionality.
    """

    def test_cocktail_creation(self):
        """
        Test that a Cocktail can be created with valid fields.
        """
        cocktail = Cocktail.objects.create(
            name="Margarita",
            description="A refreshing cocktail with lime and tequila",
            instructions="Shake all ingredients with ice and strain into a glass",
            creator=self.test_user,
            is_alcoholic=True,
            color="Yellow"
        )
        self.assertEqual(cocktail.name, "Margarita")
        self.assertEqual(cocktail.creator, self.test_user)
        self.assertTrue(cocktail.is_alcoholic)
        self.assertEqual(str(cocktail), "Margarita")

    def test_cocktail_ingredient_relationships(self):
        """
        Test many-to-many relationships between cocktails and ingredients.
        """
        cocktail = Cocktail.objects.create(
            name="Test Cocktail",
            creator=self.test_user
        )
        ingredient = Ingredient.objects.create(
            name="Lime Juice",
            ingredient_type="juice",
            alcohol_content=0.0
        )
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=ingredient,
            amount=30.0,
            unit="ml"
        )
        self.assertIn(ingredient, cocktail.ingredients.all())

    def test_cocktail_volume_and_abv(self):
        """
        Test calculation of total volume and alcohol content.
        """
        cocktail = Cocktail.objects.create(
            name="Test Cocktail",
            creator=self.test_user
        )
        ingredient1 = Ingredient.objects.create(
            name="Vodka",
            ingredient_type="spirit",
            alcohol_content=40.0
        )
        ingredient2 = Ingredient.objects.create(
            name="Orange Juice",
            ingredient_type="juice",
            alcohol_content=0.0
        )
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=ingredient1,
            amount=50.0,
            unit="ml"
        )
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=ingredient2,
            amount=100.0,
            unit="ml"
        )
        self.assertEqual(cocktail.get_total_volume(), 150.0)
        self.assertAlmostEqual(cocktail.get_alcohol_content(), 13.33, places=2)


class UserInteractionModelTest(BaseModelTest):
    """
    STEP 10: Test class for user-related functionality.
    
    Tests for features like:
    - User profiles/preferences
    - Recipe favorites/ratings
    - User-created recipes
    """
    
    def test_user_recipe_ownership(self):
        """
        STEP 11: Test that users can own and manage their recipes.
        """
        # This test will verify user-recipe relationships once models exist
        self.assertEqual(self.test_user.username, 'bartender_test')
        self.assertTrue(True, "User interaction tests ready for implementation")


class ProfileModelTest(TestCase):
    """
    Test class for Profile model functionality.
    """
    
    def setUp(self):
        self.user = User.objects.create(username="testuser")

    def test_profile_age_validation(self):
        """Test that ValidationError is raised for users under 21."""
        profile = Profile(user=self.user, birthdate=date(2010, 8, 10))
        with self.assertRaises(ValidationError):
            profile.clean()

    def test_profile_valid_age(self):
        """Test that no ValidationError is raised for users 21 or older."""
        profile = Profile(user=self.user, birthdate=date(2000, 8, 10))
        try:
            profile.clean()
        except ValidationError:
            self.fail("ValidationError raised for valid age.")


# =============================================================================
# 🧪 TEST UTILITIES AND HELPER METHODS
# =============================================================================

class TestHelpers:
    """
    STEP 12: Utility class with helper methods for creating test data.
    
    These methods can be used across different test classes to create
    consistent test objects with realistic data.
    """
    
    @staticmethod
    def create_test_ingredient(name="Test Ingredient", ingredient_type="Test"):
        """
        Helper method to create test ingredients with default values.
        Makes tests more readable and reduces code duplication.
        """
        # TODO: Implement when Ingredient model exists
        # return Ingredient.objects.create(
        #     name=name,
        #     ingredient_type=ingredient_type,
        #     alcohol_content=0.0
        # )
        pass
    
    @staticmethod
    def create_test_recipe(name="Test Recipe", user=None):
        """
        Helper method to create test recipes with sensible defaults.
        """
        # TODO: Implement when Recipe model exists
        pass


# =============================================================================
# 🧪 INTEGRATION TESTS
# =============================================================================

class StirCraftIntegrationTest(BaseModelTest):
    """
    STEP 13: Integration tests for testing multiple models working together.
    
    These tests verify that different parts of the application work correctly
    when combined, such as creating a complete recipe with ingredients,
    instructions, and user associations.
    """
    
    def test_complete_recipe_workflow(self):
        """
        STEP 14: Test the full workflow of creating a complete recipe.
        
        This test will simulate a user creating a recipe from start to finish,
        including adding ingredients, instructions, and metadata.
        """
        # TODO: Implement comprehensive workflow test
        self.assertTrue(True, "Integration tests ready for implementation")


# =============================================================================
# 🧪 PERFORMANCE TESTS (Optional)
# =============================================================================

class PerformanceTest(TestCase):
    """
    STEP 15: Optional performance tests for database queries.
    
    These tests help ensure that our models and queries perform well
    as the database grows.
    """
    
    def test_recipe_search_performance(self):
        """
        Test that recipe searches remain fast even with many recipes.
        """
        # TODO: Create many test recipes and time search operations
        self.assertTrue(True, "Performance tests ready for implementation")


# =============================================================================
# 🧪 HOW TO USE THIS TESTING FRAMEWORK:
# =============================================================================
#
# 1. As you create models in models.py, uncomment and update the corresponding
#    test methods in this file.
#
# 2. Run tests frequently during development:
#    python manage.py test stir_craft
#
# 3. Add new test methods for each model method or business logic you create.
#
# 4. Use the TestHelpers class to avoid duplicating object creation code.
#
# 5. Write tests BEFORE implementing complex features (Test-Driven Development).
#
# 6. Aim for high test coverage - every model field, method, and edge case
#    should have corresponding tests.
#
# =============================================================================

class ProfileViewTest(TestCase):
    """
    Test class for profile-related views.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            birthdate=date(2000, 8, 10)
        )

    def test_profile_detail_current_user(self):
        """Test that profile detail view displays the current user's profile."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('profile_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_profile_detail_specific_user(self):
        """Test that profile detail view displays a specific user's profile."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='password123'
        )
        other_profile = Profile.objects.create(
            user=other_user,
            birthdate=date(1990, 1, 1)
        )
        response = self.client.get(reverse('profile_detail', args=[other_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, other_user.username)

    def test_profile_update_valid_submission(self):
        """Test that profile update view successfully updates the profile."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('profile_update'), {
            'birthdate': '1999-01-01'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.birthdate, date(1999, 1, 1))

    def test_profile_update_invalid_submission(self):
        """Test that profile update view handles invalid submissions gracefully."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('profile_update'), {
            'birthdate': 'invalid-date'
        })
        self.assertEqual(response.status_code, 200)  # Stay on the form page
        self.assertContains(response, 'Please correct the errors below.')

class GeneralViewTest(TestCase):
    """
    Test class for general views.
    """

    def test_home_view(self):
        """Test that the home view renders the correct template."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stir_craft/home.html')


# =============================================================================
# 🍸 COCKTAIL FORMS TESTING FRAMEWORK
# =============================================================================

class CocktailFormTest(TestCase):
    """
    Test class for CocktailForm functionality.
    
    Tests the main cocktail creation form including validation,
    field behavior, and integration with the User model.
    """
    
    def setUp(self):
        """Set up test data for cocktail form tests."""
        self.user = User.objects.create_user(
            username='cocktail_creator',
            email='creator@stircraft.com',
            password='test_password_123'
        )
        self.vessel = Vessel.objects.create(
            name='Martini Glass',
            volume=180.0,
            material='Glass',
            stemmed=True
        )

    def test_cocktail_form_valid_data(self):
        """Test CocktailForm with valid data."""
        form_data = {
            'name': 'Classic Margarita',
            'description': 'A refreshing tequila-based cocktail',
            'instructions': 'Shake with ice and strain into glass',
            'vessel': self.vessel.id,
            'is_alcoholic': True,
            'color': 'Yellow',
            'vibe_tags': 'tropical, citrusy, refreshing'
        }
        form = CocktailForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_cocktail_form_required_fields(self):
        """Test that required fields are properly validated."""
        # Test with missing name (required field)
        form_data = {
            'description': 'A test cocktail',
            'instructions': '',  # Missing required instructions
        }
        form = CocktailForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('instructions', form.errors)

    def test_cocktail_form_optional_fields(self):
        """Test that optional fields work correctly."""
        form_data = {
            'name': 'Simple Cocktail',
            'instructions': 'Mix and serve',
            # description, vessel, color, vibe_tags are optional
        }
        form = CocktailForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_cocktail_form_user_context(self):
        """Test that form behaves correctly with user context."""
        form = CocktailForm(user=self.user)
        # Check that vessel queryset is properly set
        self.assertIn(self.vessel, form.fields['vessel'].queryset)
        # Check that help text includes user reference
        self.assertIn(self.user.username, form.fields['name'].help_text)


class RecipeComponentFormTest(TestCase):
    """
    Test class for RecipeComponentForm functionality.
    
    Tests the individual ingredient form used within the formset.
    """
    
    def setUp(self):
        """Set up test data for recipe component form tests."""
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.cocktail = Cocktail.objects.create(
            name='Test Cocktail',
            instructions='Test instructions',
            creator=self.user
        )
        self.ingredient = Ingredient.objects.create(
            name='Vodka',
            ingredient_type='spirit',
            alcohol_content=40.0
        )

    def test_recipe_component_form_valid_data(self):
        """Test RecipeComponentForm with valid data."""
        form_data = {
            'ingredient': self.ingredient.id,
            'amount': 50.0,
            'unit': 'ml',
            'preparation_note': 'Chilled',
            'order': 1
        }
        form = RecipeComponentForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_recipe_component_form_required_fields(self):
        """Test that required fields are validated."""
        form_data = {
            # Missing ingredient, amount, unit (all required)
            'preparation_note': 'Optional note',
            'order': 1
        }
        form = RecipeComponentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ingredient', form.errors)
        self.assertIn('amount', form.errors)
        self.assertIn('unit', form.errors)

    def test_recipe_component_form_amount_validation(self):
        """Test amount field validation."""
        form_data = {
            'ingredient': self.ingredient.id,
            'amount': -10.0,  # Negative amount should be invalid
            'unit': 'ml',
            'order': 1
        }
        form = RecipeComponentForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_recipe_component_form_unit_choices(self):
        """Test that unit field accepts valid choices."""
        valid_units = ['oz', 'ml', 'tsp', 'tbsp', 'dash', 'splash', 'pinch', 'piece', 'slice', 'wedge', 'sprig']
        
        for unit in valid_units:
            form_data = {
                'ingredient': self.ingredient.id,
                'amount': 30.0,
                'unit': unit,
                'order': 1
            }
            form = RecipeComponentForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Unit '{unit}' should be valid. Errors: {form.errors}")


class RecipeComponentFormsetTest(TestCase):
    """
    Test class for RecipeComponentFormSet functionality.
    
    Tests the formset that manages multiple ingredients in a cocktail.
    """
    
    def setUp(self):
        """Set up test data for formset tests."""
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.cocktail = Cocktail.objects.create(
            name='Test Cocktail',
            instructions='Test instructions',
            creator=self.user
        )
        self.vodka = Ingredient.objects.create(
            name='Vodka',
            ingredient_type='spirit',
            alcohol_content=40.0
        )
        self.juice = Ingredient.objects.create(
            name='Orange Juice',
            ingredient_type='juice',
            alcohol_content=0.0
        )

    def test_formset_minimum_forms(self):
        """Test that formset requires minimum number of forms."""
        # Empty formset should be invalid (min_num=1)
        formset_data = {
            'components-TOTAL_FORMS': '1',
            'components-INITIAL_FORMS': '0',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
            # No actual form data
        }
        formset = RecipeComponentFormSet(data=formset_data, instance=self.cocktail)
        self.assertFalse(formset.is_valid())

    def test_formset_valid_data(self):
        """Test formset with valid ingredient data."""
        formset_data = {
            'components-TOTAL_FORMS': '2',
            'components-INITIAL_FORMS': '0',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
            
            'components-0-ingredient': self.vodka.id,
            'components-0-amount': '50.0',
            'components-0-unit': 'ml',
            'components-0-preparation_note': '',
            'components-0-order': '1',
            
            'components-1-ingredient': self.juice.id,
            'components-1-amount': '100.0',
            'components-1-unit': 'ml',
            'components-1-preparation_note': 'Fresh squeezed',
            'components-1-order': '2',
        }
        formset = RecipeComponentFormSet(data=formset_data, instance=self.cocktail)
        self.assertTrue(formset.is_valid(), f"Formset errors: {formset.errors}")

    def test_formset_maximum_forms(self):
        """Test that formset enforces maximum number of forms."""
        # Create formset data with more than max_num (15) forms
        formset_data = {
            'components-TOTAL_FORMS': '16',  # More than max_num=15
            'components-INITIAL_FORMS': '0',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
        }
        # Add 16 ingredient forms
        for i in range(16):
            formset_data.update({
                f'components-{i}-ingredient': self.vodka.id,
                f'components-{i}-amount': '30.0',
                f'components-{i}-unit': 'ml',
                f'components-{i}-order': str(i + 1),
            })
        
        formset = RecipeComponentFormSet(data=formset_data, instance=self.cocktail)
        self.assertFalse(formset.is_valid())

    def test_formset_deletion(self):
        """Test formset deletion functionality."""
        # Create a cocktail with existing ingredients
        component = RecipeComponent.objects.create(
            cocktail=self.cocktail,
            ingredient=self.vodka,
            amount=50.0,
            unit='ml',
            order=1
        )
        
        formset_data = {
            'components-TOTAL_FORMS': '1',
            'components-INITIAL_FORMS': '1',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
            
            'components-0-id': component.id,
            'components-0-ingredient': self.vodka.id,
            'components-0-amount': '50.0',
            'components-0-unit': 'ml',
            'components-0-order': '1',
            'components-0-DELETE': 'on',  # Mark for deletion
        }
        
        formset = RecipeComponentFormSet(data=formset_data, instance=self.cocktail)
        # Note: This will fail validation because min_num=1 and we're deleting the only form
        self.assertFalse(formset.is_valid())


class CocktailSearchFormTest(TestCase):
    """
    Test class for CocktailSearchForm functionality.
    
    Tests the search and filter form used in cocktail browsing.
    """
    
    def setUp(self):
        """Set up test data for search form tests."""
        self.ingredient = Ingredient.objects.create(
            name='Gin',
            ingredient_type='spirit',
            alcohol_content=40.0
        )
        self.vessel = Vessel.objects.create(
            name='Coupe Glass',
            volume=150.0,
            material='Glass'
        )

    def test_search_form_empty_data(self):
        """Test search form with no data (should be valid)."""
        form = CocktailSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_search_form_text_search(self):
        """Test search form with text query."""
        form_data = {
            'query': 'margarita',
            'sort_by': '-created_at'
        }
        form = CocktailSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_search_form_filters(self):
        """Test search form with various filters."""
        form_data = {
            'ingredient': self.ingredient.id,
            'vessel': self.vessel.id,
            'is_alcoholic': 'True',
            'color': 'red',
            'sort_by': 'name'
        }
        form = CocktailSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_search_form_sort_options(self):
        """Test all sort options are valid."""
        sort_options = ['-created_at', 'created_at', 'name', '-name', 'creator__username']
        
        for sort_option in sort_options:
            form_data = {'sort_by': sort_option}
            form = CocktailSearchForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Sort option '{sort_option}' should be valid")


# =============================================================================
# 🍸 COCKTAIL VIEWS TESTING FRAMEWORK
# =============================================================================

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

    def test_cocktail_list_view(self):
        """Test cocktail list view displays correctly."""
        # Create a test cocktail
        cocktail = Cocktail.objects.create(
            name='Test Cocktail',
            instructions='Mix and serve',
            creator=self.user
        )
        
        response = self.client.get(reverse('cocktail_list'))
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
        self.assertContains(response, 'cocktail_form')
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
        self.assertIn('/accounts/login/', response.url)

    def test_cocktail_list_search_functionality(self):
        """Test search functionality in cocktail list view."""
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
        response = self.client.get(reverse('cocktail_list'), {'query': 'mary'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bloody Mary')
        self.assertNotContains(response, 'Margarita')

    def test_cocktail_list_filter_by_ingredient(self):
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
        
        response = self.client.get(reverse('cocktail_list'), {'ingredient': self.vodka.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vodka Cocktail')


# =============================================================================
# 🧪 INTEGRATION TESTS FOR COCKTAIL SYSTEM
# =============================================================================

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
        self.assertContains(response, '60 ml')
        self.assertContains(response, 'Chilled')
        
        # Step 8: Test search functionality
        response = self.client.get(reverse('cocktail_list'), {'query': 'martini'})
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
        response = self.client.get(reverse('cocktail_list'), {'is_alcoholic': 'True'})
        self.assertContains(response, 'Gin Fizz')
        self.assertNotContains(response, 'Virgin Mary')
        
        # Test filtering by ingredient
        response = self.client.get(reverse('cocktail_list'), {'ingredient': self.gin.id})
        self.assertContains(response, 'Gin Fizz')
        self.assertNotContains(response, 'Virgin Mary')
        
        # Test filtering by vessel
        response = self.client.get(reverse('cocktail_list'), {'vessel': self.martini_glass.id})
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


# =============================================================================
# 🧪 PERFORMANCE TESTS FOR COCKTAIL SYSTEM
# =============================================================================

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

    def test_cocktail_list_query_efficiency(self):
        """Test that cocktail list view uses efficient database queries."""
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
        
        # Test query count for list view
        with self.assertNumQueries(6):  # Should be efficient with select_related/prefetch_related
            response = self.client.get(reverse('cocktail_list'))
            self.assertEqual(response.status_code, 200)

    def test_cocktail_detail_query_efficiency(self):
        """Test that cocktail detail view uses efficient queries."""
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
        with self.assertNumQueries(4):  # Should be efficient
            response = self.client.get(reverse('cocktail_detail', args=[cocktail.id]))
            self.assertEqual(response.status_code, 200)

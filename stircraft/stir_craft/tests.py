from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Profile, Ingredient, Cocktail, RecipeComponent, Vessel
from datetime import date
from django.urls import reverse
from django.test import Client

# =============================================================================
# 🧪 STIR CRAFT MODEL TESTING FRAMEWORK
# =============================================================================
# 
# This file contains automated tests to validate our cocktail/mocktail app models.
# Django's testing framework creates a temporary database for each test run,
# so we can safely create, modify, and delete test data without affecting 
# our production database.
#
# HOW TO RUN TESTS:
# - Run all tests: python manage.py test
# - Run specific app tests: python manage.py test stir_craft
# - Run specific test class: python manage.py test stir_craft.tests.IngredientModelTest
# - Run with verbose output: python manage.py test --verbosity=2
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

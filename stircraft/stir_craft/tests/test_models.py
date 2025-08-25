from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from ..models import Ingredient, Cocktail, RecipeComponent, Vessel
from datetime import date


class BaseModelTest(TestCase):
    """
    Base test class with common setup for all model tests.
    
    This class provides shared functionality that other test classes can inherit.
    Using setUpTestData() instead of setUp() for better performance - it runs
    once per test class instead of once per test method.
    """
    
    @classmethod
    def setUpTestData(cls):
        """
        Create test data that will be used across multiple test methods.
        
        This method runs once when the test class is loaded, creating objects
        that can be referenced in all test methods within this class.
        """
        # Create a test user for recipes that require user ownership
        cls.test_user = User.objects.create_user(
            username='bartender_test',
            email='test@stircraft.com',
            password='test_password_123'
        )


class IngredientModelTest(BaseModelTest):
    """
    Test class for Ingredient model functionality.
    
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

    def test_cocktail_color_functionality(self):
        """
        Test cocktail color assignment and default behavior.
        """
        # Test default color
        cocktail1 = Cocktail.objects.create(
            name="Default Color Cocktail",
            creator=self.test_user
        )
        self.assertEqual(cocktail1.color, "Clear")

        # Test explicit color assignment
        cocktail2 = Cocktail.objects.create(
            name="Red Cocktail",
            creator=self.test_user,
            color="Red"
        )
        self.assertEqual(cocktail2.color, "Red")

    def test_ingredient_new_categories(self):
        """
        Test new ingredient categories from enhanced categorization.
        """
        # Test spirit category
        spirit = Ingredient.objects.create(
            name="Premium Gin",
            ingredient_type="spirit",
            alcohol_content=42.0
        )
        self.assertEqual(spirit.ingredient_type, "spirit")
        self.assertTrue(spirit.is_alcoholic())

        # Test dairy category
        dairy = Ingredient.objects.create(
            name="Heavy Cream",
            ingredient_type="dairy",
            alcohol_content=0.0
        )
        self.assertEqual(dairy.ingredient_type, "dairy")
        self.assertFalse(dairy.is_alcoholic())

        # Test garnish category
        garnish = Ingredient.objects.create(
            name="Lemon Twist",
            ingredient_type="garnish",
            alcohol_content=0.0
        )
        self.assertEqual(garnish.ingredient_type, "garnish")
        self.assertFalse(garnish.is_alcoholic())

    def test_recipe_component_display_formatting(self):
        """
        Test enhanced display formatting for recipe components.
        """
        cocktail = Cocktail.objects.create(
            name="Display Test Cocktail",
            creator=self.test_user
        )
        ingredient = Ingredient.objects.create(
            name="Test Ingredient",
            ingredient_type="spirit",
            alcohol_content=40.0
        )
        
        # Test different unit displays
        component = RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=ingredient,
            amount=30.0,
            unit="ml"
        )
        
        display = component.get_display_amount()
        self.assertIsInstance(display, str)
        self.assertIn("oz", display)  # Should convert mL to oz for display

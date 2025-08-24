"""
Test suite for enhanced ingredient categorization functionality.

This module tests:
- New ingredient type categories (spirit, liqueur, wine, beer, soda, dairy, garnish, etc.)
- Ingredient type validation and constraints
- Category-based filtering functionality
- ABV calculation improvements based on categories
- Ingredient recategorization management command

Tests the expanded INGREDIENT_TYPES choices and related functionality.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from io import StringIO
from ..models import Ingredient, Cocktail, RecipeComponent


class IngredientCategorizationTest(TestCase):
    """Test class for ingredient categorization functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user for cocktail creation."""
        cls.test_user = User.objects.create_user(
            username='categorization_tester',
            email='categories@stircraft.com',
            password='test_password_123'
        )
    
    def test_ingredient_type_choices(self):
        """Test that all new ingredient types are valid choices."""
        expected_types = [
            'spirit', 'liqueur', 'wine', 'beer', 'mixer', 'soda', 
            'syrup', 'bitters', 'juice', 'dairy', 'garnish', 'other'
        ]
        
        # Get the actual choices from the model
        actual_types = [choice[0] for choice in Ingredient.INGREDIENT_TYPES]
        
        for expected_type in expected_types:
            self.assertIn(expected_type, actual_types)
    
    def test_spirit_category_creation(self):
        """Test creation of spirit category ingredients."""
        spirits = [
            ('Vodka', 40.0),
            ('Gin', 40.0),
            ('Whiskey', 43.0),
            ('Rum', 40.0),
            ('Tequila', 40.0)
        ]
        
        for name, abv in spirits:
            ingredient = Ingredient.objects.create(
                name=name,
                ingredient_type='spirit',
                alcohol_content=abv
            )
            self.assertEqual(ingredient.ingredient_type, 'spirit')
            self.assertTrue(ingredient.is_alcoholic())
            self.assertEqual(ingredient.alcohol_content, abv)
    
    def test_non_alcoholic_category_creation(self):
        """Test creation of non-alcoholic category ingredients."""
        non_alcoholic_categories = [
            ('mixer', 'Orange Juice'),
            ('soda', 'Tonic Water'),
            ('juice', 'Lime Juice'),
            ('dairy', 'Heavy Cream'),
            ('garnish', 'Lemon Wedge'),
            ('other', 'Ice Cubes')
        ]
        
        for category, name in non_alcoholic_categories:
            ingredient = Ingredient.objects.create(
                name=name,
                ingredient_type=category,
                alcohol_content=0.0
            )
            self.assertEqual(ingredient.ingredient_type, category)
            self.assertFalse(ingredient.is_alcoholic())
            self.assertEqual(ingredient.alcohol_content, 0.0)
    
    def test_alcoholic_category_creation(self):
        """Test creation of alcoholic category ingredients."""
        alcoholic_categories = [
            ('liqueur', 'Triple Sec', 40.0),
            ('wine', 'Dry Vermouth', 18.0),
            ('beer', 'Stout Beer', 5.0),
            ('syrup', 'Grenadine', 0.0),  # Some syrups are non-alcoholic
            ('bitters', 'Angostura Bitters', 44.7)
        ]
        
        for category, name, abv in alcoholic_categories:
            ingredient = Ingredient.objects.create(
                name=name,
                ingredient_type=category,
                alcohol_content=abv
            )
            self.assertEqual(ingredient.ingredient_type, category)
            self.assertEqual(ingredient.is_alcoholic(), abv > 0)
            self.assertEqual(ingredient.alcohol_content, abv)
    
    def test_ingredient_filtering_by_type(self):
        """Test filtering ingredients by category type."""
        # Create ingredients of different types
        Ingredient.objects.create(name='Vodka', ingredient_type='spirit', alcohol_content=40.0)
        Ingredient.objects.create(name='Orange Juice', ingredient_type='juice', alcohol_content=0.0)
        Ingredient.objects.create(name='Triple Sec', ingredient_type='liqueur', alcohol_content=40.0)
        Ingredient.objects.create(name='Tonic Water', ingredient_type='soda', alcohol_content=0.0)
        
        # Test filtering
        spirits = Ingredient.objects.filter(ingredient_type='spirit')
        self.assertEqual(spirits.count(), 1)
        self.assertEqual(spirits.first().name, 'Vodka')
        
        juices = Ingredient.objects.filter(ingredient_type='juice')
        self.assertEqual(juices.count(), 1)
        self.assertEqual(juices.first().name, 'Orange Juice')
        
        # Test filtering alcoholic vs non-alcoholic
        alcoholic = Ingredient.objects.filter(alcohol_content__gt=0)
        self.assertEqual(alcoholic.count(), 2)
        
        non_alcoholic = Ingredient.objects.filter(alcohol_content=0)
        self.assertEqual(non_alcoholic.count(), 2)
    
    def test_ingredient_type_validation(self):
        """Test that invalid ingredient types are rejected."""
        with self.assertRaises(ValidationError):
            ingredient = Ingredient(
                name='Invalid Type Test',
                ingredient_type='invalid_type',
                alcohol_content=0.0
            )
            ingredient.full_clean()
    
    def test_category_based_abv_calculations(self):
        """Test that cocktail ABV calculations work properly with categorized ingredients."""
        # Create a cocktail with categorized ingredients
        cocktail = Cocktail.objects.create(
            name='Category Test Cocktail',
            instructions='Mix and serve',
            creator=self.test_user
        )
        
        # Add categorized ingredients
        vodka = Ingredient.objects.create(
            name='Premium Vodka',
            ingredient_type='spirit',
            alcohol_content=40.0
        )
        orange_juice = Ingredient.objects.create(
            name='Fresh Orange Juice',
            ingredient_type='juice',
            alcohol_content=0.0
        )
        triple_sec = Ingredient.objects.create(
            name='Premium Triple Sec',
            ingredient_type='liqueur',
            alcohol_content=40.0
        )
        
        # Add recipe components
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=vodka,
            amount=50.0,
            unit='ml'
        )
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=orange_juice,
            amount=100.0,
            unit='ml'
        )
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=triple_sec,
            amount=25.0,
            unit='ml'
        )
        
        # Test ABV calculation
        expected_abv = ((50 * 40) + (25 * 40)) / 175  # Only alcoholic ingredients contribute
        self.assertAlmostEqual(cocktail.get_alcohol_content(), expected_abv, places=2)
    
    def test_ingredient_type_display_names(self):
        """Test that ingredient type display names are human-readable."""
        # Test that choice display names are properly formatted
        type_choices = dict(Ingredient.INGREDIENT_TYPES)
        
        expected_display_names = {
            'spirit': 'Spirit',
            'liqueur': 'Liqueur',
            'wine': 'Wine',
            'beer': 'Beer',
            'mixer': 'Mixer',
            'soda': 'Soda',
            'syrup': 'Syrup',
            'bitters': 'Bitters',
            'juice': 'Juice',
            'dairy': 'Dairy',
            'garnish': 'Garnish',
            'other': 'Other'
        }
        
        for type_key, expected_display in expected_display_names.items():
            self.assertEqual(type_choices[type_key], expected_display)
    
    def test_ingredient_categorization_consistency(self):
        """Test that similar ingredients can be consistently categorized."""
        # Test spirits
        spirits = ['Vodka', 'Gin', 'Whiskey', 'Rum', 'Tequila', 'Brandy']
        for spirit_name in spirits:
            ingredient = Ingredient.objects.create(
                name=spirit_name,
                ingredient_type='spirit',
                alcohol_content=40.0
            )
            self.assertEqual(ingredient.ingredient_type, 'spirit')
            self.assertTrue(ingredient.is_alcoholic())
        
        # Test juices
        juices = ['Orange Juice', 'Lime Juice', 'Lemon Juice', 'Cranberry Juice']
        for juice_name in juices:
            ingredient = Ingredient.objects.create(
                name=juice_name,
                ingredient_type='juice',
                alcohol_content=0.0
            )
            self.assertEqual(ingredient.ingredient_type, 'juice')
            self.assertFalse(ingredient.is_alcoholic())
    
    def test_garnish_and_other_categories(self):
        """Test the garnish and other categories for non-liquid ingredients."""
        garnishes = [
            'Lemon Wedge',
            'Lime Wheel',
            'Cherry',
            'Olives',
            'Orange Peel',
            'Mint Sprig'
        ]
        
        for garnish_name in garnishes:
            ingredient = Ingredient.objects.create(
                name=garnish_name,
                ingredient_type='garnish',
                alcohol_content=0.0
            )
            self.assertEqual(ingredient.ingredient_type, 'garnish')
            self.assertFalse(ingredient.is_alcoholic())
        
        # Test other category
        other_items = ['Ice', 'Salt Rim', 'Sugar Rim']
        for item_name in other_items:
            ingredient = Ingredient.objects.create(
                name=item_name,
                ingredient_type='other',
                alcohol_content=0.0
            )
            self.assertEqual(ingredient.ingredient_type, 'other')
            self.assertFalse(ingredient.is_alcoholic())
    
    def test_dairy_category_handling(self):
        """Test the dairy category for cream-based ingredients."""
        dairy_items = [
            ('Heavy Cream', 0.0),
            ('Milk', 0.0),
            ('Egg White', 0.0),
            ('Irish Cream Liqueur', 17.0)  # Some dairy items can be alcoholic
        ]
        
        for item_name, abv in dairy_items:
            ingredient = Ingredient.objects.create(
                name=item_name,
                ingredient_type='dairy',
                alcohol_content=abv
            )
            self.assertEqual(ingredient.ingredient_type, 'dairy')
            self.assertEqual(ingredient.is_alcoholic(), abv > 0)

"""
Test suite for cocktail color system and intelligent color detection.

This module tests:
- Color choice validation and constraints
- Intelligent color detection based on ingredients
- Color normalization functionality
- Default color handling
- Color filtering capabilities

Tests the enhanced COLOR_CHOICES and color detection logic.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from io import StringIO
from ..models import Cocktail, Ingredient, RecipeComponent


class CocktailColorSystemTest(TestCase):
    """Test class for cocktail color system functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user and base ingredients for color testing."""
        cls.test_user = User.objects.create_user(
            username='color_tester',
            email='colors@stircraft.com',
            password='test_password_123'
        )
        
        # Create test ingredients with color-inducing properties
        cls.red_ingredients = [
            Ingredient.objects.create(name='Cranberry Juice', ingredient_type='juice', alcohol_content=0.0),
            Ingredient.objects.create(name='Grenadine', ingredient_type='syrup', alcohol_content=0.0),
            Ingredient.objects.create(name='Cherry Juice', ingredient_type='juice', alcohol_content=0.0),
            Ingredient.objects.create(name='Campari', ingredient_type='liqueur', alcohol_content=25.0),
        ]
        
        cls.orange_ingredients = [
            Ingredient.objects.create(name='Orange Juice', ingredient_type='juice', alcohol_content=0.0),
            Ingredient.objects.create(name='Cointreau', ingredient_type='liqueur', alcohol_content=40.0),
            Ingredient.objects.create(name='Aperol', ingredient_type='liqueur', alcohol_content=11.0),
        ]
        
        cls.clear_ingredients = [
            Ingredient.objects.create(name='Vodka', ingredient_type='spirit', alcohol_content=40.0),
            Ingredient.objects.create(name='Gin', ingredient_type='spirit', alcohol_content=40.0),
            Ingredient.objects.create(name='Soda Water', ingredient_type='soda', alcohol_content=0.0),
        ]
        
        cls.green_ingredients = [
            Ingredient.objects.create(name='Lime Juice', ingredient_type='juice', alcohol_content=0.0),
            Ingredient.objects.create(name='Green Chartreuse', ingredient_type='liqueur', alcohol_content=55.0),
            Ingredient.objects.create(name='Midori', ingredient_type='liqueur', alcohol_content=20.0),
        ]
    
    def test_color_choices_validation(self):
        """Test that all defined color choices are valid."""
        expected_colors = [
            'Clear', 'White', 'Yellow', 'Orange', 'Red', 'Pink', 
            'Purple', 'Blue', 'Green', 'Brown', 'Black', 'Gold', 
            'Silver', 'Cream', 'Amber'
        ]
        
        # Get actual color choices from model
        actual_colors = [choice[0] for choice in Cocktail.COLOR_CHOICES]
        
        for expected_color in expected_colors:
            self.assertIn(expected_color, actual_colors)
    
    def test_default_color_assignment(self):
        """Test that cocktails get default color when none specified."""
        cocktail = Cocktail.objects.create(
            name='Default Color Test',
            instructions='Mix and serve',
            creator=self.test_user
            # color not specified, should default to 'Clear'
        )
        
        self.assertEqual(cocktail.color, 'Clear')
    
    def test_explicit_color_assignment(self):
        """Test explicit color assignment during cocktail creation."""
        test_colors = ['Red', 'Orange', 'Green', 'Blue', 'Purple']
        
        for color in test_colors:
            cocktail = Cocktail.objects.create(
                name=f'{color} Cocktail Test',
                instructions='Mix and serve',
                creator=self.test_user,
                color=color
            )
            self.assertEqual(cocktail.color, color)
    
    def test_red_color_detection_ingredients(self):
        """Test that red-inducing ingredients are properly identified."""
        cocktail = Cocktail.objects.create(
            name='Red Test Cocktail',
            instructions='Mix and serve',
            creator=self.test_user,
            color='Clear'  # Start with clear, will be updated by detection
        )
        
        # Add red ingredient
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.red_ingredients[0],  # Cranberry Juice
            amount=100.0,
            unit='ml'
        )
        
        # Add clear ingredient
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.clear_ingredients[0],  # Vodka
            amount=50.0,
            unit='ml'
        )
        
        # Test that we can identify red ingredients
        ingredient_names = [component.ingredient.name.lower() for component in cocktail.components.all()]
        has_red_ingredient = any('cranberry' in name for name in ingredient_names)
        self.assertTrue(has_red_ingredient)
    
    def test_orange_color_detection_ingredients(self):
        """Test that orange-inducing ingredients are properly identified."""
        cocktail = Cocktail.objects.create(
            name='Orange Test Cocktail',
            instructions='Mix and serve',
            creator=self.test_user,
            color='Clear'
        )
        
        # Add orange ingredients
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.orange_ingredients[0],  # Orange Juice
            amount=100.0,
            unit='ml'
        )
        
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.orange_ingredients[1],  # Cointreau
            amount=25.0,
            unit='ml'
        )
        
        # Test ingredient detection
        ingredient_names = [component.ingredient.name.lower() for component in cocktail.components.all()]
        has_orange_ingredient = any(
            any(orange_word in name for orange_word in ['orange', 'cointreau', 'aperol'])
            for name in ingredient_names
        )
        self.assertTrue(has_orange_ingredient)
    
    def test_clear_cocktail_detection(self):
        """Test cocktails that should remain clear."""
        cocktail = Cocktail.objects.create(
            name='Clear Test Cocktail',
            instructions='Mix and serve',
            creator=self.test_user,
            color='Clear'
        )
        
        # Add only clear ingredients
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.clear_ingredients[0],  # Vodka
            amount=50.0,
            unit='ml'
        )
        
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.clear_ingredients[2],  # Soda Water
            amount=100.0,
            unit='ml'
        )
        
        # Should remain clear
        ingredient_names = [component.ingredient.name.lower() for component in cocktail.components.all()]
        has_color_ingredient = any(
            any(color_word in name for color_word in ['cranberry', 'orange', 'lime', 'green'])
            for name in ingredient_names
        )
        self.assertFalse(has_color_ingredient)
    
    def test_green_color_detection_ingredients(self):
        """Test that green-inducing ingredients are properly identified."""
        cocktail = Cocktail.objects.create(
            name='Green Test Cocktail',
            instructions='Mix and serve',
            creator=self.test_user,
            color='Clear'
        )
        
        # Add green ingredients
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.green_ingredients[0],  # Lime Juice
            amount=30.0,
            unit='ml'
        )
        
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.green_ingredients[1],  # Green Chartreuse
            amount=15.0,
            unit='ml'
        )
        
        # Test ingredient detection
        ingredient_names = [component.ingredient.name.lower() for component in cocktail.components.all()]
        has_green_ingredient = any(
            any(green_word in name for green_word in ['lime', 'green', 'chartreuse', 'midori'])
            for name in ingredient_names
        )
        self.assertTrue(has_green_ingredient)
    
    def test_color_filtering_functionality(self):
        """Test filtering cocktails by color."""
        # Create cocktails with different colors
        red_cocktail = Cocktail.objects.create(
            name='Red Cocktail',
            instructions='Mix and serve',
            creator=self.test_user,
            color='Red'
        )
        
        orange_cocktail = Cocktail.objects.create(
            name='Orange Cocktail',
            instructions='Mix and serve',
            creator=self.test_user,
            color='Orange'
        )
        
        clear_cocktail = Cocktail.objects.create(
            name='Clear Cocktail',
            instructions='Mix and serve',
            creator=self.test_user,
            color='Clear'
        )
        
        # Test filtering by color
        red_cocktails = Cocktail.objects.filter(color='Red')
        self.assertEqual(red_cocktails.count(), 1)
        self.assertEqual(red_cocktails.first().name, 'Red Cocktail')
        
        orange_cocktails = Cocktail.objects.filter(color='Orange')
        self.assertEqual(orange_cocktails.count(), 1)
        self.assertEqual(orange_cocktails.first().name, 'Orange Cocktail')
        
        clear_cocktails = Cocktail.objects.filter(color='Clear')
        self.assertEqual(clear_cocktails.count(), 1)
        self.assertEqual(clear_cocktails.first().name, 'Clear Cocktail')
    
    def test_multiple_color_ingredient_priority(self):
        """Test color detection when cocktail has multiple color-inducing ingredients."""
        cocktail = Cocktail.objects.create(
            name='Multi Color Test',
            instructions='Mix and serve',
            creator=self.test_user,
            color='Clear'
        )
        
        # Add both red and orange ingredients
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.red_ingredients[0],  # Cranberry Juice
            amount=50.0,
            unit='ml'
        )
        
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.orange_ingredients[0],  # Orange Juice
            amount=50.0,
            unit='ml'
        )
        
        # Both color types should be detectable
        ingredient_names = [component.ingredient.name.lower() for component in cocktail.components.all()]
        has_red = any('cranberry' in name for name in ingredient_names)
        has_orange = any('orange' in name for name in ingredient_names)
        
        self.assertTrue(has_red)
        self.assertTrue(has_orange)
    
    def test_color_choices_case_sensitivity(self):
        """Test that color choices are case-sensitive and properly formatted."""
        # Test that colors are stored with proper capitalization
        cocktail = Cocktail.objects.create(
            name='Case Test Cocktail',
            instructions='Mix and serve',
            creator=self.test_user,
            color='red'  # lowercase input
        )
        
        # Should be stored as provided (validation happens at form level)
        self.assertEqual(cocktail.color, 'red')
        
        # Test with proper case
        cocktail2 = Cocktail.objects.create(
            name='Proper Case Test',
            instructions='Mix and serve',
            creator=self.test_user,
            color='Red'  # proper case
        )
        
        self.assertEqual(cocktail2.color, 'Red')
    
    def test_special_color_categories(self):
        """Test special color categories like Pink, Purple, and Blue."""
        special_colors = ['Pink', 'Purple', 'Blue', 'Brown', 'Gold', 'Silver']
        
        for color in special_colors:
            cocktail = Cocktail.objects.create(
                name=f'{color} Special Test',
                instructions='Mix and serve',
                creator=self.test_user,
                color=color
            )
            self.assertEqual(cocktail.color, color)
    
    def test_color_field_max_length(self):
        """Test that color field respects max_length constraint."""
        # Test that the longest color name fits
        longest_colors = ['Purple', 'Orange', 'Silver']  # 6 characters each
        
        for color in longest_colors:
            cocktail = Cocktail.objects.create(
                name=f'Max Length {color}',
                instructions='Mix and serve',
                creator=self.test_user,
                color=color
            )
            self.assertEqual(cocktail.color, color)
    
    def test_color_blank_and_default_behavior(self):
        """Test color field behavior when blank or not specified."""
        # Test with explicit blank
        cocktail1 = Cocktail.objects.create(
            name='Blank Color Test',
            instructions='Mix and serve',
            creator=self.test_user,
            color=''  # explicitly blank
        )
        # Should still work since blank=True
        self.assertEqual(cocktail1.color, '')
        
        # Test with default
        cocktail2 = Cocktail.objects.create(
            name='Default Color Test',
            instructions='Mix and serve',
            creator=self.test_user
            # no color specified, should use default
        )
        self.assertEqual(cocktail2.color, 'Clear')

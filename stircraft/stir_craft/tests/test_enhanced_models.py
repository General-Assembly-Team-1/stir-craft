"""
Enhanced test suite for updated model functionality from the image handling feature.

This module tests new and enhanced model features:
- Enhanced Cocktail model with image field and color system
- Improved ABV calculations with proper ingredient categorization  
- Updated RecipeComponent with unit standardization
- Enhanced Ingredient model with expanded categories
- Color detection and display methods

This supplements the existing test_models.py with new functionality.
"""

import tempfile
from decimal import Decimal
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Cocktail, Ingredient, RecipeComponent, Vessel


# Use a temporary directory for test media files
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class EnhancedModelTest(TestCase):
    """Enhanced test class for updated model functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Create comprehensive test data for enhanced model testing."""
        cls.test_user = User.objects.create_user(
            username='enhanced_model_tester',
            email='enhanced@stircraft.com',
            password='test_password_123'
        )
        
        # Create test vessel
        cls.test_vessel = Vessel.objects.create(
            name='Test Glass',
            volume=240.0,
            material='Glass',
            stemmed=False
        )
        
        # Create ingredients with new categorization system
        cls.premium_vodka = Ingredient.objects.create(
            name='Premium Vodka',
            ingredient_type='spirit',
            alcohol_content=40.0,
            description='High-quality vodka for cocktails'
        )
        
        cls.cranberry_juice = Ingredient.objects.create(
            name='Cranberry Juice',
            ingredient_type='juice',
            alcohol_content=0.0,
            description='Fresh cranberry juice'
        )
        
        cls.triple_sec = Ingredient.objects.create(
            name='Triple Sec',
            ingredient_type='liqueur',
            alcohol_content=40.0,
            description='Orange-flavored liqueur'
        )
        
        cls.lime_juice = Ingredient.objects.create(
            name='Fresh Lime Juice',
            ingredient_type='juice',
            alcohol_content=0.0,
            description='Freshly squeezed lime juice'
        )
        
        cls.heavy_cream = Ingredient.objects.create(
            name='Heavy Cream',
            ingredient_type='dairy',
            alcohol_content=0.0,
            description='Heavy whipping cream'
        )
        
        cls.mint_sprig = Ingredient.objects.create(
            name='Fresh Mint Sprig',
            ingredient_type='garnish',
            alcohol_content=0.0,
            description='Fresh mint for garnish'
        )
    
    def test_enhanced_cocktail_creation_with_new_fields(self):
        """Test cocktail creation with all new enhanced fields."""
        cocktail = Cocktail.objects.create(
            name='Enhanced Test Cocktail',
            description='A cocktail to test enhanced functionality',
            instructions='Shake with ice and strain',
            creator=self.test_user,
            vessel=self.test_vessel,
            is_alcoholic=True,
            color='Red'
        )
        
        # Test basic properties
        self.assertEqual(cocktail.name, 'Enhanced Test Cocktail')
        self.assertEqual(cocktail.color, 'Red')
        self.assertTrue(cocktail.is_alcoholic)
        self.assertEqual(cocktail.vessel, self.test_vessel)
        
        # Test image-related methods with no image
        self.assertFalse(cocktail.has_image())
        self.assertIsNone(cocktail.get_image_url())
    
    def test_cocktail_with_all_new_color_choices(self):
        """Test cocktail creation with all new color choices."""
        color_choices = [
            'Clear', 'White', 'Yellow', 'Orange', 'Red', 'Pink',
            'Purple', 'Blue', 'Green', 'Brown', 'Black', 'Gold',
            'Silver', 'Cream', 'Amber'
        ]
        
        for color in color_choices:
            with self.subTest(color=color):
                cocktail = Cocktail.objects.create(
                    name=f'{color} Test Cocktail',
                    instructions='Test instructions',
                    creator=self.test_user,
                    color=color
                )
                self.assertEqual(cocktail.color, color)
    
    def test_enhanced_abv_calculation_with_categorized_ingredients(self):
        """Test improved ABV calculation with properly categorized ingredients."""
        cocktail = Cocktail.objects.create(
            name='ABV Test Cocktail',
            instructions='Mix and serve',
            creator=self.test_user
        )
        
        # Add ingredients with different categories and ABV levels
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.premium_vodka,  # 40% ABV spirit
            amount=60.0,
            unit='ml'
        )
        
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.triple_sec,  # 40% ABV liqueur
            amount=20.0,
            unit='ml'
        )
        
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.cranberry_juice,  # 0% ABV juice
            amount=80.0,
            unit='ml'
        )
        
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.lime_juice,  # 0% ABV juice
            amount=20.0,
            unit='ml'
        )
        
        # Calculate expected ABV
        # Alcoholic volume: (60 * 0.40) + (20 * 0.40) = 24 + 8 = 32 mL alcohol
        # Total volume: 60 + 20 + 80 + 20 = 180 mL
        # ABV: (32 / 180) * 100 = 17.78%
        expected_abv = (32.0 / 180.0) * 100
        
        calculated_abv = cocktail.get_alcohol_content()
        self.assertAlmostEqual(calculated_abv, expected_abv, places=2)
    
    def test_ingredient_enhanced_categorization(self):
        """Test the enhanced ingredient categorization system."""
        # Test all new ingredient types
        test_categories = [
            ('spirit', self.premium_vodka),
            ('juice', self.cranberry_juice),
            ('liqueur', self.triple_sec),
            ('dairy', self.heavy_cream),
            ('garnish', self.mint_sprig)
        ]
        
        for expected_category, ingredient in test_categories:
            with self.subTest(category=expected_category):
                self.assertEqual(ingredient.ingredient_type, expected_category)
                
                # Test is_alcoholic method works correctly
                if expected_category in ['spirit', 'liqueur']:
                    self.assertTrue(ingredient.is_alcoholic())
                else:
                    self.assertFalse(ingredient.is_alcoholic())
    
    def test_recipe_component_enhanced_unit_handling(self):
        """Test enhanced unit handling in RecipeComponent."""
        cocktail = Cocktail.objects.create(
            name='Unit Test Cocktail',
            instructions='Test instructions',
            creator=self.test_user
        )
        
        # Test different unit types
        unit_test_cases = [
            (50.0, 'ml', self.premium_vodka),
            (1.5, 'oz', self.triple_sec),
            (0.5, 'tsp', self.lime_juice),
            (2, 'dash', self.mint_sprig),
            (1, 'splash', self.cranberry_juice),
        ]
        
        for amount, unit, ingredient in unit_test_cases:
            with self.subTest(unit=unit):
                component = RecipeComponent.objects.create(
                    cocktail=cocktail,
                    ingredient=ingredient,
                    amount=Decimal(str(amount)),
                    unit=unit
                )
                
                # Test basic properties
                self.assertEqual(component.amount, Decimal(str(amount)))
                self.assertEqual(component.unit, unit)
                
                # Test display amount method exists and returns string
                display_amount = component.get_display_amount()
                self.assertIsInstance(display_amount, str)
                
                # Test storage amount conversion method
                storage_ml = component.get_storage_amount_ml()
                self.assertIsInstance(storage_ml, float)
                self.assertGreater(storage_ml, 0)
    
    def test_recipe_component_order_and_preparation_notes(self):
        """Test order and preparation note functionality."""
        cocktail = Cocktail.objects.create(
            name='Ordered Cocktail',
            instructions='Follow the order',
            creator=self.test_user
        )
        
        # Create components with specific order and notes
        component1 = RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.premium_vodka,
            amount=50.0,
            unit='ml',
            order=1,
            preparation_note='Add first'
        )
        
        component2 = RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.cranberry_juice,
            amount=100.0,
            unit='ml',
            order=2,
            preparation_note='Add slowly'
        )
        
        component3 = RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.mint_sprig,
            amount=1,
            unit='sprig',
            order=3,
            preparation_note='Garnish on top'
        )
        
        # Test order is preserved
        components = cocktail.components.all().order_by('order')
        self.assertEqual(components[0], component1)
        self.assertEqual(components[1], component2)
        self.assertEqual(components[2], component3)
        
        # Test preparation notes
        self.assertEqual(component1.preparation_note, 'Add first')
        self.assertEqual(component2.preparation_note, 'Add slowly')
        self.assertEqual(component3.preparation_note, 'Garnish on top')
    
    def test_cocktail_total_volume_calculation(self):
        """Test total volume calculation with mixed units."""
        cocktail = Cocktail.objects.create(
            name='Volume Test Cocktail',
            instructions='Test volume calculation',
            creator=self.test_user
        )
        
        # Add components with different units
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.premium_vodka,
            amount=50.0,
            unit='ml'
        )
        
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.cranberry_juice,
            amount=100.0,
            unit='ml'
        )
        
        RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.lime_juice,
            amount=1.0,
            unit='oz'  # Should be included in volume calculation
        )
        
        total_volume = cocktail.get_total_volume()
        
        # Should include all measurable components
        # 50 + 100 + 1.0 = 151.0 (oz is stored as oz for this test)
        expected_volume = 50.0 + 100.0 + 1.0
        self.assertEqual(total_volume, expected_volume)
    
    def test_cocktail_forking_functionality(self):
        """Test cocktail forking (recipe variations)."""
        # Create original cocktail
        original = Cocktail.objects.create(
            name='Original Margarita',
            instructions='Classic margarita recipe',
            creator=self.test_user,
            color='Yellow'
        )
        
        # Create forked version
        forked = Cocktail.objects.create(
            name='Cranberry Margarita',
            instructions='Margarita with cranberry twist',
            creator=self.test_user,
            forked_from=original,
            color='Red'
        )
        
        # Test forking relationship
        self.assertEqual(forked.forked_from, original)
        self.assertIn(forked, original.forks.all())
    
    def test_ingredient_flavor_tags_functionality(self):
        """Test flavor tags using TaggableManager."""
        # Test adding flavor tags to ingredient
        self.premium_vodka.flavor_tags.add('clean', 'neutral', 'smooth')
        self.lime_juice.flavor_tags.add('citrusy', 'tart', 'fresh')
        
        # Test tag retrieval
        vodka_tags = list(self.premium_vodka.flavor_tags.names())
        self.assertIn('clean', vodka_tags)
        self.assertIn('neutral', vodka_tags)
        self.assertIn('smooth', vodka_tags)
        
        lime_tags = list(self.lime_juice.flavor_tags.names())
        self.assertIn('citrusy', lime_tags)
        self.assertIn('tart', lime_tags)
        self.assertIn('fresh', lime_tags)
    
    def test_cocktail_vibe_tags_functionality(self):
        """Test vibe tags on cocktails using TaggableManager."""
        cocktail = Cocktail.objects.create(
            name='Tropical Sunset',
            instructions='Mix and garnish',
            creator=self.test_user,
            color='Orange'
        )
        
        # Add vibe tags
        cocktail.vibe_tags.add('tropical', 'summer', 'fruity', 'refreshing')
        
        # Test tag retrieval
        vibe_tags = list(cocktail.vibe_tags.names())
        expected_tags = ['tropical', 'summer', 'fruity', 'refreshing']
        
        for tag in expected_tags:
            self.assertIn(tag, vibe_tags)
    
    def test_ingredient_timestamps(self):
        """Test that ingredient timestamps are properly set."""
        # Test that created_at and updated_at are set
        self.assertIsNotNone(self.premium_vodka.created_at)
        self.assertIsNotNone(self.premium_vodka.updated_at)
        
        # Test that updated_at changes on save
        original_updated = self.premium_vodka.updated_at
        self.premium_vodka.description = 'Updated description'
        self.premium_vodka.save()
        
        self.premium_vodka.refresh_from_db()
        self.assertGreater(self.premium_vodka.updated_at, original_updated)
    
    def test_cocktail_timestamps(self):
        """Test that cocktail timestamps are properly set."""
        cocktail = Cocktail.objects.create(
            name='Timestamp Test',
            instructions='Test timestamps',
            creator=self.test_user
        )
        
        # Test that timestamps are set
        self.assertIsNotNone(cocktail.created_at)
        self.assertIsNotNone(cocktail.updated_at)
        
        # Test ordering by creation date (newest first)
        cocktails = Cocktail.objects.all()
        if len(cocktails) > 1:
            # Should be ordered by -created_at (newest first)
            for i in range(len(cocktails) - 1):
                self.assertGreaterEqual(cocktails[i].created_at, cocktails[i + 1].created_at)
    
    def test_non_alcoholic_property_on_recipe_component(self):
        """Test the non_alcoholic property on RecipeComponent."""
        cocktail = Cocktail.objects.create(
            name='Mixed Drink',
            instructions='Test non-alcoholic property',
            creator=self.test_user
        )
        
        # Add alcoholic component
        alcoholic_component = RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.premium_vodka,  # 40% ABV
            amount=50.0,
            unit='ml'
        )
        
        # Add non-alcoholic component
        non_alcoholic_component = RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=self.cranberry_juice,  # 0% ABV
            amount=100.0,
            unit='ml'
        )
        
        # Test non_alcoholic property
        self.assertFalse(alcoholic_component.non_alcoholic)
        self.assertTrue(non_alcoholic_component.non_alcoholic)

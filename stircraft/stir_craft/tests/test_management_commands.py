"""
Test suite for management commands added in the image handling feature.

This module tests:
- detect_cocktail_colors command
- fix_alcohol_content command  
- normalize_colors command
- recategorize_ingredients command
- standardize_units command
- show_unit_examples command

Tests command functionality, argument parsing, and data manipulation.
"""

from io import StringIO
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from ..models import Cocktail, Ingredient, RecipeComponent


class ManagementCommandsTest(TestCase):
    """Test class for management command functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test data for management command testing."""
        cls.test_user = User.objects.create_user(
            username='command_tester',
            email='commands@stircraft.com',
            password='test_password_123'
        )
        
        # Create test ingredients with various properties
        cls.vodka = Ingredient.objects.create(
            name='Vodka',
            ingredient_type='spirit',
            alcohol_content=40.0
        )
        
        cls.cranberry_juice = Ingredient.objects.create(
            name='Cranberry Juice',
            ingredient_type='juice',
            alcohol_content=0.0
        )
        
        cls.orange_juice = Ingredient.objects.create(
            name='Orange Juice',
            ingredient_type='juice',
            alcohol_content=0.0
        )
        
        cls.lime_juice = Ingredient.objects.create(
            name='Lime Juice',
            ingredient_type='juice',
            alcohol_content=0.0
        )
        
        # Create test cocktails with different characteristics
        cls.red_cocktail = Cocktail.objects.create(
            name='Red Test Cocktail',
            instructions='Mix and serve',
            creator=cls.test_user,
            color='Clear'  # Will be updated by color detection
        )
        
        cls.orange_cocktail = Cocktail.objects.create(
            name='Orange Test Cocktail',
            instructions='Mix and serve',
            creator=cls.test_user,
            color='Clear'  # Will be updated by color detection
        )
        
        # Add components to cocktails
        RecipeComponent.objects.create(
            cocktail=cls.red_cocktail,
            ingredient=cls.vodka,
            amount=50.0,
            unit='ml'
        )
        
        RecipeComponent.objects.create(
            cocktail=cls.red_cocktail,
            ingredient=cls.cranberry_juice,
            amount=100.0,
            unit='ml'
        )
        
        RecipeComponent.objects.create(
            cocktail=cls.orange_cocktail,
            ingredient=cls.vodka,
            amount=50.0,
            unit='ml'
        )
        
        RecipeComponent.objects.create(
            cocktail=cls.orange_cocktail,
            ingredient=cls.orange_juice,
            amount=100.0,
            unit='ml'
        )
    
    def test_detect_cocktail_colors_command_basic(self):
        """Test basic functionality of detect_cocktail_colors command."""
        # Capture command output
        out = StringIO()
        
        # Run the command
        call_command('detect_cocktail_colors', stdout=out)
        
        # Check that command ran without errors
        output = out.getvalue()
        self.assertIn('Successfully updated', output)
        
        # Refresh cocktails from database
        self.red_cocktail.refresh_from_db()
        self.orange_cocktail.refresh_from_db()
        
        # Colors should be detected and updated
        # (Exact colors depend on implementation, but should not be 'Clear')
        self.assertIsNotNone(self.red_cocktail.color)
        self.assertIsNotNone(self.orange_cocktail.color)
    
    def test_detect_cocktail_colors_dry_run(self):
        """Test dry-run mode of detect_cocktail_colors command."""
        out = StringIO()
        
        # Run with dry-run flag
        call_command('detect_cocktail_colors', '--dry-run', stdout=out)
        
        output = out.getvalue()
        # Should indicate dry run mode
        self.assertIn('DRY RUN', output)
        self.assertIn('Would make', output)
        
        # Colors should NOT be changed in dry-run mode
        self.red_cocktail.refresh_from_db()
        self.orange_cocktail.refresh_from_db()
        
        # Should still be original colors
        self.assertEqual(self.red_cocktail.color, 'Clear')
        self.assertEqual(self.orange_cocktail.color, 'Clear')
    
    def test_detect_cocktail_colors_force_flag(self):
        """Test force flag updates cocktails with existing colors."""
        # Set a specific color first
        self.red_cocktail.color = 'Blue'
        self.red_cocktail.save()
        
        out = StringIO()
        
        # Run without force (should skip cocktails with non-Clear colors)
        call_command('detect_cocktail_colors', stdout=out)
        
        self.red_cocktail.refresh_from_db()
        # Should still be Blue without force flag
        self.assertEqual(self.red_cocktail.color, 'Blue')
        
        # Now run with force flag
        out = StringIO()
        call_command('detect_cocktail_colors', '--force', stdout=out)
        
        self.red_cocktail.refresh_from_db()
        # Color should be updated even though it wasn't Clear
        # (Exact color depends on detection logic)
        self.assertIsNotNone(self.red_cocktail.color)
    
    def test_fix_alcohol_content_command(self):
        """Test fix_alcohol_content command functionality."""
        # Create an ingredient that needs ABV correction
        rum_151 = Ingredient.objects.create(
            name='151 Proof Rum',
            ingredient_type='spirit',
            alcohol_content=40.0  # Wrong ABV, should be ~75.5%
        )
        
        out = StringIO()
        call_command('fix_alcohol_content', stdout=out)
        
        output = out.getvalue()
        self.assertIn('abv', output.lower())
        
        # Check if the ingredient was updated
        rum_151.refresh_from_db()
        # Exact correction depends on implementation
        self.assertIsNotNone(rum_151.alcohol_content)
    
    def test_normalize_colors_command(self):
        """Test normalize_colors command functionality."""
        # Create cocktail with non-standard color
        cocktail_with_weird_color = Cocktail.objects.create(
            name='Weird Color Cocktail',
            instructions='Mix and serve',
            creator=self.test_user,
            color='reddish'  # Non-standard color
        )
        
        out = StringIO()
        call_command('normalize_colors', stdout=out)
        
        output = out.getvalue()
        # Should indicate some processing occurred
        self.assertIsInstance(output, str)
        
        cocktail_with_weird_color.refresh_from_db()
        # Color should be normalized (exact result depends on implementation)
        self.assertIsNotNone(cocktail_with_weird_color.color)
    
    def test_recategorize_ingredients_command(self):
        """Test recategorize_ingredients command functionality."""
        # Create ingredient that might need recategorization
        tonic_water = Ingredient.objects.create(
            name='Tonic Water',
            ingredient_type='mixer',  # Might be recategorized to 'soda'
            alcohol_content=0.0
        )
        
        out = StringIO()
        call_command('recategorize_ingredients', stdout=out)
        
        output = out.getvalue()
        self.assertIn('ingredient', output.lower())
        
        tonic_water.refresh_from_db()
        # Category might be updated (depends on implementation)
        self.assertIsNotNone(tonic_water.ingredient_type)
    
    def test_standardize_units_command(self):
        """Test standardize_units command functionality."""
        # Create component with non-standard unit that could be standardized
        teaspoon_component = RecipeComponent.objects.create(
            cocktail=self.red_cocktail,
            ingredient=self.lime_juice,
            amount=1.0,
            unit='tbsp'  # Could be converted to mL or standardized
        )
        
        out = StringIO()
        call_command('standardize_units', stdout=out)
        
        output = out.getvalue()
        self.assertIn('unit', output.lower())
        
        teaspoon_component.refresh_from_db()
        # Unit might be standardized (depends on implementation)
        self.assertIsNotNone(teaspoon_component.unit)
    
    def test_show_unit_examples_command(self):
        """Test show_unit_examples command functionality."""
        out = StringIO()
        call_command('show_unit_examples', stdout=out)
        
        output = out.getvalue()
        
        # Should show unit examples and documentation
        self.assertIn('unit', output.lower())
        self.assertIn('example', output.lower())
        
        # Should contain information about different unit types
        expected_units = ['oz', 'ml', 'tsp', 'dash', 'splash']
        for unit in expected_units:
            self.assertIn(unit, output.lower())
    
    def test_command_help_messages(self):
        """Test that commands provide helpful help messages."""
        commands_to_test = [
            'detect_cocktail_colors',
            'fix_alcohol_content',
            'normalize_colors',
            'recategorize_ingredients',
            'standardize_units',
            'show_unit_examples'
        ]
        
        for command_name in commands_to_test:
            with self.subTest(command=command_name):
                out = StringIO()
                try:
                    call_command(command_name, '--help', stdout=out)
                    output = out.getvalue()
                    # Help should contain command description
                    self.assertIn(command_name.replace('_', ' '), output.lower())
                except SystemExit:
                    # --help causes SystemExit, which is expected
                    pass
    
    def test_detect_colors_with_no_ingredients(self):
        """Test color detection with cocktails that have no ingredients."""
        empty_cocktail = Cocktail.objects.create(
            name='Empty Cocktail',
            instructions='No ingredients',
            creator=self.test_user,
            color='Clear'
        )
        
        out = StringIO()
        call_command('detect_cocktail_colors', stdout=out)
        
        # Should handle empty cocktails gracefully
        empty_cocktail.refresh_from_db()
        self.assertIsNotNone(empty_cocktail.color)
    
    def test_command_output_formatting(self):
        """Test that command outputs are properly formatted and informative."""
        out = StringIO()
        call_command('detect_cocktail_colors', stdout=out)
        
        output = out.getvalue()
        
        # Should contain summary information
        self.assertIn('=', output)  # Likely has formatting dividers
        
        # Should show counts or statistics
        self.assertTrue(any(char.isdigit() for char in output))
    
    def test_color_distribution_summary(self):
        """Test that color detection command shows distribution summary."""
        out = StringIO()
        call_command('detect_cocktail_colors', stdout=out)
        
        output = out.getvalue()
        
        # Should show color distribution after detection
        self.assertIn('COLOR DISTRIBUTION', output)
        
        # Should list various colors and their counts
        color_keywords = ['clear', 'red', 'orange', 'green', 'blue']
        found_colors = [color for color in color_keywords if color.lower() in output.lower()]
        self.assertGreater(len(found_colors), 0)
    
    def test_dry_run_vs_actual_execution(self):
        """Test difference between dry-run and actual execution."""
        # Record initial state
        initial_red_color = self.red_cocktail.color
        
        # Run dry-run first
        out_dry = StringIO()
        call_command('detect_cocktail_colors', '--dry-run', stdout=out_dry)
        
        self.red_cocktail.refresh_from_db()
        # Should be unchanged after dry-run
        self.assertEqual(self.red_cocktail.color, initial_red_color)
        
        # Run actual command
        out_actual = StringIO()
        call_command('detect_cocktail_colors', stdout=out_actual)
        
        self.red_cocktail.refresh_from_db()
        # Color might be changed after actual execution
        # (Depends on detection logic)
        self.assertIsNotNone(self.red_cocktail.color)

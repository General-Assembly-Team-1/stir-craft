"""
Template Tags Tests for StirCraft

This module tests Django template tags and filters including:
- Math filters (multiplication, smart rounding, formatting)
- Template tag registration and loading
- Edge cases and error handling
- Template integration functionality

Author: StirCraft Development Team
Date: August 2025
"""

from django.test import TestCase
from django.template import Context, Template
from django.template.loader import get_template
from decimal import Decimal
import math

from ...templatetags.math_filters import mul, smart_round, format_amount


class MathFiltersTest(TestCase):
    """Test mathematical template filters."""
    
    def test_mul_filter_basic_functionality(self):
        """Test basic multiplication functionality."""
        # Test with integers
        result = mul(5, 3)
        self.assertEqual(result, 15.0)
        
        # Test with floats
        result = mul(2.5, 4.0)
        self.assertEqual(result, 10.0)
        
        # Test with strings that represent numbers
        result = mul("3", "7")
        self.assertEqual(result, 21.0)
        
        # Test with mixed types
        result = mul(4, "2.5")
        self.assertEqual(result, 10.0)
    
    def test_mul_filter_edge_cases(self):
        """Test multiplication filter with edge cases."""
        # Test with zero
        result = mul(0, 5)
        self.assertEqual(result, 0.0)
        
        result = mul(10, 0)
        self.assertEqual(result, 0.0)
        
        # Test with negative numbers
        result = mul(-3, 4)
        self.assertEqual(result, -12.0)
        
        result = mul(-2, -5)
        self.assertEqual(result, 10.0)
        
        # Test with decimal values
        result = mul(0.1, 0.2)
        self.assertAlmostEqual(result, 0.02, places=10)
        
        # Test with large numbers
        result = mul(1000000, 2)
        self.assertEqual(result, 2000000.0)
    
    def test_mul_filter_error_handling(self):
        """Test multiplication filter error handling."""
        # Test with invalid input
        result = mul("invalid", 5)
        self.assertEqual(result, '')
        
        result = mul(5, "not_a_number")
        self.assertEqual(result, '')
        
        # Test with None values
        result = mul(None, 5)
        self.assertEqual(result, '')
        
        result = mul(5, None)
        self.assertEqual(result, '')
        
        # Test with empty strings
        result = mul("", 5)
        self.assertEqual(result, '')
        
        # Test with boolean values (should work as they convert to numbers)
        result = mul(True, 5)
        self.assertEqual(result, 5.0)
        
        result = mul(False, 10)
        self.assertEqual(result, 0.0)
    
    def test_smart_round_with_ml(self):
        """Test smart rounding with milliliter units."""
        # Test whole number mL
        result = smart_round(50.0, 'ml')
        self.assertEqual(result, 50)
        
        # Test decimal mL - should round to whole number
        result = smart_round(45.7, 'ml')
        self.assertEqual(result, 46)
        
        result = smart_round(30.3, 'ml')
        self.assertEqual(result, 30)
        
        # Test with ML (uppercase)
        result = smart_round(75.6, 'ML')
        self.assertEqual(result, 76)
        
        # Test with milliliter spelled out
        result = smart_round(100.8, 'milliliter')
        self.assertEqual(result, 101)  # 100.8 rounds to 101
    
    def test_smart_round_with_ounces(self):
        """Test smart rounding with ounce units."""
        # Test whole number oz
        result = smart_round(2.0, 'oz')
        self.assertEqual(result, 2)
        
        # Test decimal oz - should round to 1 decimal place
        result = smart_round(1.75, 'oz')
        self.assertEqual(result, 1.8)
        
        result = smart_round(0.5, 'oz')
        self.assertEqual(result, 0.5)
        
        # Test with different oz variations
        result = smart_round(3.14, 'fl oz')
        self.assertEqual(result, 3.1)
        
        result = smart_round(2.67, 'ounce')
        self.assertEqual(result, 2.7)
        
        result = smart_round(1.99, 'ounces')
        self.assertEqual(result, 2)  # Should show as integer when it rounds to whole
    
    def test_smart_round_with_other_units(self):
        """Test smart rounding with other units."""
        # Test with teaspoons
        result = smart_round(1.75, 'tsp')
        self.assertEqual(result, 1.8)
        
        # Test with tablespoons  
        result = smart_round(0.66, 'tbsp')
        self.assertEqual(result, 0.7)
        
        # Test with dash
        result = smart_round(2.3, 'dash')
        self.assertEqual(result, 2.3)
        
        # Test with no unit specified
        result = smart_round(3.14, None)
        self.assertEqual(result, 3.1)
        
        # Test with empty unit
        result = smart_round(2.67, '')
        self.assertEqual(result, 2.7)
    
    def test_smart_round_edge_cases(self):
        """Test smart rounding with edge cases."""
        # Test with very small numbers
        result = smart_round(0.001, 'oz')
        self.assertEqual(result, 0)
        
        # Test with very large numbers
        result = smart_round(999.99, 'ml')
        self.assertEqual(result, 1000)
        
        # Test with negative numbers
        result = smart_round(-1.5, 'oz')
        self.assertEqual(result, -1.5)
        
        # Test with zero
        result = smart_round(0, 'ml')
        self.assertEqual(result, 0)
    
    def test_smart_round_error_handling(self):
        """Test smart rounding error handling."""
        # Test with invalid input
        result = smart_round("invalid", 'oz')
        self.assertEqual(result, "invalid")
        
        # Test with None
        result = smart_round(None, 'ml')
        self.assertEqual(result, None)
        
        # Test with empty string
        result = smart_round("", 'oz')
        self.assertEqual(result, "")
        
        # Test with boolean
        result = smart_round(True, 'ml')
        self.assertEqual(result, 1)
    
    def test_format_amount_basic_functionality(self):
        """Test basic amount formatting."""
        # Test whole numbers
        result = format_amount(5.0)
        self.assertEqual(result, 5)
        
        result = format_amount(10)
        self.assertEqual(result, 10)
        
        # Test decimals
        # Test basic functionality
        result = format_amount(2.5)
        self.assertEqual(result, '2.5')
        
        result = format_amount(1.75)
        self.assertEqual(result, '1.75')
        
        # Test very precise decimals - should remove trailing zeros
        result = format_amount(3.14159)
        self.assertEqual(result, '3.14159')
        
        result = format_amount(2.50000)
        self.assertEqual(result, '2.5')
    
    def test_format_amount_edge_cases(self):
        """Test amount formatting edge cases."""
        # Test zero
        result = format_amount(0.0)
        self.assertEqual(result, 0)
        
        # Test negative numbers
        result = format_amount(-1.5)
        self.assertEqual(result, '-1.5')
        
        result = format_amount(-2.0)
        self.assertEqual(result, -2)
        
        # Test very small numbers
        result = format_amount(0.001)
        self.assertEqual(result, '0.001')
        
        # Test numbers that should round
        result = format_amount(1.0000000001)
        self.assertEqual(result, '1')
    
    def test_format_amount_error_handling(self):
        """Test amount formatting error handling."""
        # Test with invalid input
        result = format_amount("invalid")
        self.assertEqual(result, "invalid")
        
        # Test with None
        result = format_amount(None)
        self.assertEqual(result, None)
        
        # Test with empty string
        result = format_amount("")
        self.assertEqual(result, "")
        
        # Test with boolean
        result = format_amount(True)
        self.assertEqual(result, 1)
        
        result = format_amount(False)
        self.assertEqual(result, 0)


class TemplateIntegrationTest(TestCase):
    """Test template filter integration with Django templates."""
    
    def test_mul_filter_in_template(self):
        """Test multiplication filter in template context."""
        template = Template('{% load math_filters %}{{ value|mul:multiplier }}')
        
        # Test with valid values
        context = Context({'value': 3, 'multiplier': 4})
        result = template.render(context)
        self.assertEqual(result, '12.0')
        
        # Test with string values
        context = Context({'value': '2.5', 'multiplier': '4'})
        result = template.render(context)
        self.assertEqual(result, '10.0')
        
        # Test with invalid values
        context = Context({'value': 'invalid', 'multiplier': 5})
        result = template.render(context)
        self.assertEqual(result, '')
    
    def test_smart_round_filter_in_template(self):
        """Test smart round filter in template context."""
        template = Template('{% load math_filters %}{{ amount|smart_round:unit }}')
        
        # Test with mL unit
        context = Context({'amount': 45.7, 'unit': 'ml'})
        result = template.render(context)
        self.assertEqual(result, '46')
        
        # Test with oz unit
        context = Context({'amount': 1.75, 'unit': 'oz'})
        result = template.render(context)
        self.assertEqual(result, '1.8')
        
        # Test without unit
        template_no_unit = Template('{% load math_filters %}{{ amount|smart_round }}')
        context = Context({'amount': 3.14})
        result = template_no_unit.render(context)
        self.assertEqual(result, '3.1')
    
    def test_format_amount_filter_in_template(self):
        """Test format amount filter in template context."""
        template = Template('{% load math_filters %}{{ amount|format_amount }}')
        
        # Test whole number
        context = Context({'amount': 5.0})
        result = template.render(context)
        self.assertEqual(result, '5')
        
        # Test decimal
        context = Context({'amount': 2.5})
        result = template.render(context)
        self.assertEqual(result, '2.5')
        
        # Test with trailing zeros
        context = Context({'amount': 3.50000})
        result = template.render(context)
        self.assertEqual(result, '3.5')
    
    def test_chained_filters_in_template(self):
        """Test chaining multiple math filters."""
        template = Template('{% load math_filters %}{{ base|mul:multiplier|smart_round:unit|format_amount }}')
        
        # Test chained filters: multiply, round, format
        context = Context({
            'base': 1.5,
            'multiplier': 3,
            'unit': 'oz'
        })
        result = template.render(context)
        # 1.5 * 3 = 4.5, rounded to 1 decimal for oz = 4.5, formatted = 4.5
        self.assertEqual(result, '4.5')
        
        # Test with mL unit
        context = Context({
            'base': 2.3,
            'multiplier': 2,
            'unit': 'ml'
        })
        result = template.render(context)
        # 2.3 * 2 = 4.6, rounded to whole for ml = 5, formatted = 5
        self.assertEqual(result, '5')
    
    def test_filters_with_recipe_context(self):
        """Test filters in realistic cocktail recipe context."""
        template = Template('''
        {% load math_filters %}
        Recipe (serving {{ servings }}):
        {% for component in components %}
        - {{ component.amount|mul:servings|smart_round:component.unit|format_amount }} {{ component.unit }} {{ component.name }}
        {% endfor %}
        ''')
        
        context = Context({
            'servings': 2,
            'components': [
                {'name': 'Vodka', 'amount': 1.5, 'unit': 'oz'},
                {'name': 'Cranberry Juice', 'amount': 100, 'unit': 'ml'},
                {'name': 'Lime Juice', 'amount': 0.5, 'unit': 'oz'},
            ]
        })
        
        result = template.render(context)
        
        # Check that calculations are correct
        self.assertIn('3 oz Vodka', result)        # 1.5 * 2 = 3.0 oz, rounded to whole
        self.assertIn('200 ml Cranberry', result)  # 100 * 2 = 200 ml, rounded to whole
        self.assertIn('1 oz Lime', result)         # 0.5 * 2 = 1.0 oz, formatted as integer
    
    def test_template_loading_and_registration(self):
        """Test that template tags load correctly."""
        # Test that the templatetags module can be loaded
        template = Template('{% load math_filters %}Loaded successfully')
        result = template.render(Context())
        self.assertEqual(result, 'Loaded successfully')
        
        # Test that all filters are registered
        template = Template('''
        {% load math_filters %}
        {{ "5"|mul:"3" }}|{{ "45.7"|smart_round:"ml" }}|{{ "2.50"|format_amount }}
        ''')
        result = template.render(Context())
        # Should output: 15.0|46|2.5
        self.assertIn('15.0', result)
        self.assertIn('46', result)
        self.assertIn('2.5', result)
    
    def test_filters_with_none_values_in_template(self):
        """Test filter behavior with None values in templates."""
        template = Template('{% load math_filters %}{{ value|mul:multiplier }}')
        
        # Test with None value
        context = Context({'value': None, 'multiplier': 5})
        result = template.render(context)
        self.assertEqual(result, '')
        
        # Test with missing context variable
        context = Context({'multiplier': 5})
        result = template.render(context)
        self.assertEqual(result, '')
    
    def test_complex_recipe_scaling(self):
        """Test complex recipe scaling scenario."""
        template = Template('''
        {% load math_filters %}
        {# Scale a recipe by a factor and format appropriately #}
        {% for ingredient in recipe.ingredients %}
        {{ ingredient.amount|mul:scale_factor|smart_round:ingredient.unit|format_amount }} {{ ingredient.unit }} {{ ingredient.name }}{% if not forloop.last %}, {% endif %}
        {% endfor %}
        ''')
        
        context = Context({
            'scale_factor': 1.5,
            'recipe': {
                'ingredients': [
                    {'name': 'Bourbon', 'amount': 2, 'unit': 'oz'},
                    {'name': 'Simple Syrup', 'amount': 15, 'unit': 'ml'},
                    {'name': 'Angostura Bitters', 'amount': 3, 'unit': 'dash'},
                ]
            }
        })
        
        result = template.render(context)
        
        # Verify calculations:
        # Bourbon: 2 * 1.5 = 3.0 oz → 3 oz (whole number for clean display)
        # Syrup: 15 * 1.5 = 22.5 ml → 22 ml (smart_round for ml rounds 22.5 to 22)
        # Bitters: 3 * 1.5 = 4.5 dash → 4.5 dash (1 decimal for other units)
        self.assertIn('3 oz Bourbon', result)
        self.assertIn('22 ml Simple Syrup', result)
        self.assertIn('4.5 dash Angostura Bitters', result)

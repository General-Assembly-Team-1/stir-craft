"""
StirCraft Mathematical Template Filters Module

This module provides custom Django template filters for performing mathematical
operations and number formatting within cocktail recipe templates. These filters
are essential for dynamic recipe scaling, unit conversions, and presentation
formatting throughout the StirCraft application.

Mathematical Context:
Cocktail recipes require precise mathematical operations for:
- Recipe scaling (adjusting serving sizes)
- Unit conversions (ml ↔ oz)
- Display formatting (removing unnecessary decimals)
- Measurement calculations (totals, percentages)

Filter Functions:
1. mul: Safe multiplication for recipe scaling
2. smart_round: Context-aware rounding based on measurement units
3. format_amount: Intelligent decimal place formatting

Usage in Templates:
    {% load math_filters %}
    {{ ingredient.amount|mul:scale_factor }}
    {{ volume|smart_round:"ml" }}
    {{ measurement|format_amount }}

Author: StirCraft Development Team
Date: August 2025
Version: 1.0
"""

from django import template

register = template.Library()

@register.filter(name='mul')
def mul(value, arg):
    """
    Perform safe multiplication for recipe scaling and calculations.
    
    Mathematical Framework:
    This filter implements type-safe multiplication with comprehensive error
    handling for template-based mathematical operations. It's designed to
    handle the variety of numeric formats encountered in cocktail recipes.
    
    Algorithm:
    1. Type Coercion: Convert inputs to float for decimal precision
    2. Multiplication: Perform standard arithmetic multiplication
    3. Error Handling: Return empty string on any conversion/calculation failure
    4. Template Safety: Ensures templates never crash due to math errors
    
    Use Cases:
    - Recipe scaling: {{ ingredient.amount|mul:serving_multiplier }}
    - Total calculations: {{ base_volume|mul:concentration_factor }}
    - Percentage calculations: {{ ingredient_amount|mul:100 }}
    - Unit conversions: {{ ounces|mul:29.5735 }} (oz to ml)
    
    Type Handling:
    - Integers: Direct conversion to float
    - Floats: No conversion needed
    - Strings: Parsed as numeric values
    - Decimal objects: Converted to float
    - Invalid inputs: Return empty string (template-safe)
    
    Args:
        value: First multiplicand (any numeric type or string)
        arg: Second multiplicand (any numeric type or string)
        
    Returns:
        float: Product of value × arg
        str: Empty string if conversion/calculation fails
        
    Examples:
        {{ 2|mul:3 }} → 6.0
        {{ "1.5"|mul:"2" }} → 3.0
        {{ ingredient.amount|mul:scale_factor }} → scaled amount
        {{ "invalid"|mul:2 }} → "" (safe failure)
    """
    try:
        # PSEUDO-CODE: Safe multiplication algorithm
        # TRY:
        #     numeric_value = convert_to_float(value)
        #     numeric_arg = convert_to_float(arg)
        #     result = numeric_value * numeric_arg
        #     RETURN result
        # CATCH any_exception:
        #     RETURN empty_string  // Template-safe failure
        
        v = float(value)
        a = float(arg)
        return v * a
    except Exception:
        return ''

@register.filter(name='smart_round')
def smart_round(value, unit=None):
    """
    Implement context-aware rounding based on measurement unit conventions.
    
    Mathematical Framework:
    This filter applies unit-specific rounding rules that align with real-world
    bartending practices and measurement precision standards. Different units
    require different levels of precision for practical use.
    
    Rounding Rules Algorithm:
    1. Unit Classification: Categorize measurement unit type
    2. Precision Mapping: Apply appropriate decimal precision
    3. Whole Number Detection: Convert to integer when appropriate
    4. Error Handling: Return original value on parsing failures
    
    Unit-Specific Precision Standards:
    - Milliliters (ml): Round to whole numbers (bartending precision)
    - Ounces (oz): Round to 1 decimal place (standard cocktail precision)
    - Fluid Ounces (fl oz): Round to 1 decimal place (same as ounces)
    - Other units: Default to 1 decimal place (general precision)
    
    Mathematical Justification:
    - Milliliters: Bartenders measure to nearest ml in practice
    - Ounces: Standard jigger precision is 0.1 oz increments
    - Mixed units: Balance between precision and usability
    
    Integer Conversion Logic:
    Numbers that equal their integer value (e.g., 3.0) are displayed
    as integers (3) for cleaner presentation.
    
    Args:
        value: Numeric value to round (any numeric type)
        unit: Measurement unit string for context-aware rounding
        
    Returns:
        int: Whole number when value equals its integer equivalent
        float: Decimal number rounded to appropriate precision
        original: Original value if parsing fails
        
    Examples:
        {{ 30.7|smart_round:"ml" }} → 31 (whole ml)
        {{ 1.75|smart_round:"oz" }} → 1.8 (0.1 oz precision)
        {{ 2.0|smart_round:"oz" }} → 2 (integer display)
        {{ 15.234|smart_round:"tsp" }} → 15.2 (1 decimal default)
    """
    try:
        num = float(value)
        
        # PSEUDO-CODE: Context-aware rounding algorithm
        # numeric_value = convert_to_float(value)
        # 
        # IF unit_contains("ml" OR "milliliter"):
        #     RETURN round_to_whole_number(numeric_value)
        # ELIF unit_contains("oz" OR "ounce"):
        #     rounded = round_to_one_decimal(numeric_value)
        #     RETURN remove_trailing_zero_if_whole(rounded)
        # ELSE:
        #     rounded = round_to_one_decimal(numeric_value)
        #     RETURN remove_trailing_zero_if_whole(rounded)
        
        # Milliliters: Round to whole numbers (bartending precision)
        if unit and ('ml' in unit.lower() or 'milliliter' in unit.lower()):
            return int(round(num))
        
        # Ounces: Round to 1 decimal place (standard cocktail precision)
        elif unit and ('oz' in unit.lower() or 'ounce' in unit.lower()):
            rounded = round(num, 1)
            # Convert to integer if it's a whole number for cleaner display
            return int(rounded) if rounded == int(rounded) else rounded
        
        # Other units: Default to 1 decimal place
        else:
            rounded = round(num, 1)
            return int(rounded) if rounded == int(rounded) else rounded
            
    except (ValueError, TypeError):
        return value

@register.filter(name='format_amount')
def format_amount(value):
    """
    Apply intelligent decimal formatting for clean measurement display.
    
    Mathematical Framework:
    This filter implements dynamic decimal precision that removes unnecessary
    trailing zeros while preserving significant digits. It's designed to
    optimize readability in recipe displays.
    
    Formatting Algorithm:
    1. Type Conversion: Convert input to float for numeric operations
    2. Whole Number Detection: Check if value equals its integer equivalent
    3. Integer Display: Show whole numbers without decimal points
    4. Minimal Precision: Use minimal decimal places for non-whole numbers
    5. Trailing Zero Removal: Eliminate unnecessary trailing zeros
    
    Display Optimization Logic:
    - Whole numbers: 3.0 → 3 (cleaner appearance)
    - Minimal decimals: 1.500 → 1.5 (remove trailing zeros)
    - Significant digits: 1.25 → 1.25 (preserve precision)
    - Scientific notation: Avoided for typical cocktail ranges
    
    Technical Implementation:
    Uses Python's 'g' format specifier with high precision (10 digits)
    to automatically remove trailing zeros while preserving significant
    digits for the range of values typical in cocktail measurements.
    
    Args:
        value: Numeric value to format (any numeric type or string)
        
    Returns:
        int: Whole number when value equals its integer equivalent
        str: Formatted decimal string with minimal precision
        original: Original value if conversion fails
        
    Examples:
        {{ 3.0|format_amount }} → 3
        {{ 1.500|format_amount }} → 1.5
        {{ 2.25|format_amount }} → 2.25
        {{ 0.125|format_amount }} → 0.125
        {{ "invalid"|format_amount }} → "invalid"
    """
    try:
        num = float(value)
        
        # PSEUDO-CODE: Intelligent formatting algorithm
        # numeric_value = convert_to_float(value)
        # 
        # IF numeric_value == integer_equivalent(numeric_value):
        #     RETURN integer_display(numeric_value)
        # ELSE:
        #     RETURN minimal_decimal_display(numeric_value)
        
        # If it's a whole number, display as integer (cleaner appearance)
        if num == int(num):
            return int(num)
        # Otherwise, use minimal decimal precision (removes trailing zeros)
        return f"{num:.10g}"  # 'g' format removes trailing zeros automatically
    except (ValueError, TypeError):
        return value

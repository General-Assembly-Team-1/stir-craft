from django import template

register = template.Library()

@register.filter(name='mul')
def mul(value, arg):
    """Multiply value by arg safely.

    Both value and arg can be numbers or numeric strings. Returns a float
    when multiplication succeeds; otherwise returns empty string to avoid
    template exceptions.
    """
    try:
        v = float(value)
        a = float(arg)
        return v * a
    except Exception:
        return ''

@register.filter(name='smart_round')
def smart_round(value, unit=None):
    """Smart rounding for cocktail measurements.
    
    - ml: Round to nearest whole number
    - oz/fl oz: Round to 1 decimal place
    - Other units: Round to 1 decimal place
    """
    try:
        num = float(value)
        
        # For milliliters, round to whole numbers
        if unit and 'ml' in unit.lower():
            return int(round(num))
        
        # For ounces, round to 1 decimal place
        elif unit and ('oz' in unit.lower() or 'ounce' in unit.lower()):
            rounded = round(num, 1)
            # Remove trailing zero if it's a whole number
            return int(rounded) if rounded == int(rounded) else rounded
        
        # For other units, round to 1 decimal place
        else:
            rounded = round(num, 1)
            return int(rounded) if rounded == int(rounded) else rounded
            
    except (ValueError, TypeError):
        return value

@register.filter(name='format_amount')
def format_amount(value):
    """Format amounts nicely - remove unnecessary decimal places."""
    try:
        num = float(value)
        # If it's a whole number, show as integer
        if num == int(num):
            return int(num)
        # Otherwise, show with minimal decimal places
        return f"{num:.10g}"  # This removes trailing zeros
    except (ValueError, TypeError):
        return value

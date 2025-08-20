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

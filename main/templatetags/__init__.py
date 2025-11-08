import numpy as np
from django import template

register = template.Library()

@register.filter
def pow10format(value):
    """
    Formats a number in scientific notation as: 1.23 × 10¹⁵
    Usage in template: {{ value|pow10format }}
    """
    try:
        value = float(value)
        if value == 0:
            return "0"
        exp = int(np.floor(np.log10(abs(value))))
        coeff = value / 10**exp
        return f"{coeff:.2f} × 10<sup>{exp}</sup>"
    except (ValueError, TypeError):
        return str(value)

@register.filter(is_safe=True)  # Marks output as safe for HTML
def scientific(value):
    """Alternative simpler scientific notation"""
    try:
        return "{:.2e}".format(float(value))
    except (ValueError, TypeError):
        return str(value)
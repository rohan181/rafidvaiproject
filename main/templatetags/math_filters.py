import numpy as np
from django import template

register = template.Library()

@register.filter
def pow10format(value):
    try:
        value = float(value)
        if value == 0:
            return "0"
        exp = int(np.floor(np.log10(abs(value))))
        coeff = value / 10**exp
        return f"{coeff:.2f} × 10<sup>{exp}</sup>"
    except:
        return str(value)
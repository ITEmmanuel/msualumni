from django import template
from django.utils.html import format_html

# Register the template library
register = template.Library()

@register.filter
def placeholder(value):
    """Simple passthrough filter so the library is recognised.
    You can add real custom filters later.
    """
    return value

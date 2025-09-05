from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def format_birthday_message(template_obj, alumni):
    """Format birthday message with alumni data"""
    if not template_obj or not alumni:
        return "Happy Birthday!"
    
    try:
        alumni_name = f"{alumni.first_name} {alumni.last_name}".strip()
        if hasattr(alumni, 'date_of_birth') and alumni.date_of_birth:
            birthday_date = alumni.date_of_birth.strftime("%B %d")
        else:
            birthday_date = "today"
        
        formatted_message = template_obj.message.format(
            name=alumni_name,
            birthday_date=birthday_date
        )
        return mark_safe(formatted_message)
    except (AttributeError, KeyError, ValueError) as e:
        # Fallback message if formatting fails
        return f"Happy Birthday {alumni.first_name} {alumni.last_name}! 🎉"

@register.filter
def birthday_date_format(date_obj):
    """Format birthday date for display"""
    if not date_obj:
        return "today"
    return date_obj.strftime("%B %d")

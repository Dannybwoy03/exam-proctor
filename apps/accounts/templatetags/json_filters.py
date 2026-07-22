import json

from django import template
from django.utils.html import escape

register = template.Library()


@register.filter
def json_attribute(value):
    """Serialize a value for use in an HTML data-* attribute."""
    return escape(json.dumps(value))

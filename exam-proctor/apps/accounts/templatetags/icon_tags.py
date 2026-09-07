from django import template
from django.templatetags.static import static
from django.utils.html import format_html

register = template.Library()

SIZE_MAP = {
    "sm": 16,
    "md": 20,
    "lg": 32,
    "xl": 40,
}


@register.simple_tag
def icon(name, alt="", css_class="portal-icon", size="md", decorative=True):
    """Deprecated: prefer {% include "includes/icon.html" with name="..." only %}."""
    px = SIZE_MAP.get(size, 20)
    path = static(f"icons/flaticon/{name}.svg")
    classes = f"{css_class} portal-icon--{size}" if size in SIZE_MAP else css_class
    if decorative and not alt:
        return format_html(
            '<img src="{}" class="{}" width="{}" height="{}" loading="lazy" alt="" aria-hidden="true">',
            path,
            classes,
            px,
            px,
        )
    return format_html(
        '<img src="{}" class="{}" width="{}" height="{}" loading="lazy" alt="{}">',
        path,
        classes,
        px,
        px,
        alt,
    )

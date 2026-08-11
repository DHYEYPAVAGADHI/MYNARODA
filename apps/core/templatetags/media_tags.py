from django import template
from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def get_image_url(image_field, fallback_name="hero-1"):
    """
    Returns the URL of the image_field if it exists and has a url.
    Otherwise, returns the static URL of the fallback WebP image.
    Usage: {% get_image_url slide.image 'hero-1' %}
    """
    if image_field and hasattr(image_field, 'url'):
        try:
            return image_field.url
        except ValueError:
            pass
            
    return static(f"images/default/{fallback_name}.webp")

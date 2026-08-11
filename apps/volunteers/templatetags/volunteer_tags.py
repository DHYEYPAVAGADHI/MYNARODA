from django import template
from apps.volunteers.models import Organization

register = template.Library()



@register.simple_tag
def get_pledge_organizations():
    return Organization.objects.filter(is_active=True).order_by("sort_order", "name")


from django import template
from apps.competitions.models import CompetitionOrganizationType

register = template.Library()

@register.simple_tag
def get_competition_organization_types():
    return CompetitionOrganizationType.objects.filter(is_active=True).order_by("sort_order", "name")

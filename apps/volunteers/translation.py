from modeltranslation.translator import register, TranslationOptions
from .models import Organization

@register(Organization)
class OrganizationTranslationOptions(TranslationOptions):
    fields = ('name',)

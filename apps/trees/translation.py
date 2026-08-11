from modeltranslation.translator import register, TranslationOptions
from .models import TreeSpecies, Tree

@register(TreeSpecies)
class TreeSpeciesTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Tree)
class TreeTranslationOptions(TranslationOptions):
    fields = ('location_name',)

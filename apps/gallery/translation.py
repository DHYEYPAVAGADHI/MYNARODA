from modeltranslation.translator import register, TranslationOptions
from .models import GalleryCategory, Photo, GalleryCollection

@register(GalleryCategory)
class GalleryCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Photo)
class PhotoTranslationOptions(TranslationOptions):
    fields = ('title', 'location')

@register(GalleryCollection)
class GalleryCollectionTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

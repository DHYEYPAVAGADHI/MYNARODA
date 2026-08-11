from modeltranslation.translator import register, TranslationOptions
from .models import NewsCategory, NewsArticle, Document

@register(NewsCategory)
class NewsCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(NewsArticle)
class NewsArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'summary', 'content')

@register(Document)
class DocumentTranslationOptions(TranslationOptions):
    fields = ('title',)

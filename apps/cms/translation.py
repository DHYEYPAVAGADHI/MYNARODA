from modeltranslation.translator import register, TranslationOptions
from .models import SiteSettings, Testimonial, Homepage, HeroSlide
from .models_pages import PageMission, PageObjective, PageHighlight, PageActivity, PageStatistic, PageTimeline

@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = ('hero_tagline', 'campaign_title', 'popup_message')

@register(Testimonial)
class TestimonialTranslationOptions(TranslationOptions):
    fields = ('role', 'quote')

@register(Homepage)
class HomepageTranslationOptions(TranslationOptions):
    fields = (
        'hero_title', 'hero_subtitle', 'hero_description',
        'green_card_title', 'green_card_text',
        'clean_card_title', 'clean_card_text',
        'hero_background', 'green_card_image', 'clean_card_image'
    )

@register(HeroSlide)
class HeroSlideTranslationOptions(TranslationOptions):
    fields = (
        'title', 'subtitle', 'description',
        'primary_button_text', 'secondary_button_text',
        'image'
    )

@register(PageMission)
class PageMissionTranslationOptions(TranslationOptions):
    fields = (
        'title', 'hero_title', 'hero_subtitle', 'hero_description',
        'intro_title', 'intro_text_1', 'intro_text_2',
        'vision_title', 'vision_text', 'meta_title', 'meta_description',
        'hero_background', 'intro_image', 'vision_image'
    )

@register(PageObjective)
class PageObjectiveTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'image')

@register(PageHighlight)
class PageHighlightTranslationOptions(TranslationOptions):
    fields = ('badge_text', 'title', 'description', 'image')

@register(PageActivity)
class PageActivityTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'button_text', 'image')

@register(PageStatistic)
class PageStatisticTranslationOptions(TranslationOptions):
    fields = ('value', 'label', 'image')

@register(PageTimeline)
class PageTimelineTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'image')

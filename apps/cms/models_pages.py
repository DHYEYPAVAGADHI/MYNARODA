from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from .models_media import MediaAsset

class PageMission(TimeStampedModel):
    """
    Base model for dynamic mission pages (Green Naroda, Clean Naroda).
    """
    title = models.CharField(_("page title"), max_length=100)
    slug = models.SlugField(_("slug"), unique=True)
    
    # Hero Section
    hero_title = models.CharField(_("hero title"), max_length=150)
    hero_subtitle = models.CharField(_("hero subtitle"), max_length=200)
    hero_description = models.TextField(_("hero description"), blank=True)
    hero_background = models.ForeignKey(
        MediaAsset, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="hero_pages", verbose_name=_("hero background")
    )
    
    # Mission Intro
    intro_title = models.CharField(_("intro title"), max_length=150, default="Mission Introduction")
    intro_text_1 = models.TextField(_("intro paragraph 1"))
    intro_text_2 = models.TextField(_("intro paragraph 2"), blank=True)
    intro_image = models.ForeignKey(
        MediaAsset, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="intro_pages", verbose_name=_("intro image")
    )
    
    # Mission Vision
    vision_title = models.CharField(_("vision title"), max_length=150, default="The Vision")
    vision_text = models.TextField(_("vision description"))
    vision_image = models.ForeignKey(
        MediaAsset, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="vision_pages", verbose_name=_("vision image")
    )
    
    # SEO
    meta_title = models.CharField(_("meta title"), max_length=150, blank=True)
    meta_description = models.TextField(_("meta description"), blank=True)

    class Meta:
        verbose_name = _("mission page")
        verbose_name_plural = _("mission pages")

    def __str__(self):
        return self.title


class PageObjective(TimeStampedModel):
    page = models.ForeignKey(PageMission, on_delete=models.CASCADE, related_name="objectives")
    title = models.CharField(_("title"), max_length=100)
    description = models.TextField(_("description"))
    image = models.ForeignKey(MediaAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name="objectives")
    sort_order = models.PositiveSmallIntegerField(_("sort order"), default=0)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = _("objective")
        verbose_name_plural = _("objectives")


class PageHighlight(TimeStampedModel):
    page = models.ForeignKey(PageMission, on_delete=models.CASCADE, related_name="highlights")
    badge_text = models.CharField(_("badge text"), max_length=50, default="Ongoing Action")
    title = models.CharField(_("title"), max_length=150)
    description = models.TextField(_("description"))
    image = models.ForeignKey(MediaAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name="highlights")
    sort_order = models.PositiveSmallIntegerField(_("sort order"), default=0)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = _("mission highlight")
        verbose_name_plural = _("mission highlights")


class PageActivity(TimeStampedModel):
    page = models.ForeignKey(PageMission, on_delete=models.CASCADE, related_name="activities")
    title = models.CharField(_("title"), max_length=150)
    description = models.TextField(_("description"))
    button_text = models.CharField(_("button text"), max_length=50, default="Learn More")
    image = models.ForeignKey(MediaAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    sort_order = models.PositiveSmallIntegerField(_("sort order"), default=0)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = _("campaign activity")
        verbose_name_plural = _("campaign activities")


class PageStatistic(TimeStampedModel):
    page = models.ForeignKey(PageMission, on_delete=models.CASCADE, related_name="statistics")
    value = models.CharField(_("value (e.g. 100%)"), max_length=50)
    label = models.CharField(_("label"), max_length=100)
    image = models.ForeignKey(MediaAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name="statistics")
    sort_order = models.PositiveSmallIntegerField(_("sort order"), default=0)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = _("impact statistic")
        verbose_name_plural = _("impact statistics")


class PageTimeline(TimeStampedModel):
    page = models.ForeignKey(PageMission, on_delete=models.CASCADE, related_name="timelines")
    step_number = models.PositiveSmallIntegerField(_("step number"))
    title = models.CharField(_("title"), max_length=100)
    description = models.CharField(_("description"), max_length=200)
    is_active = models.BooleanField(_("is active step"), default=False)
    image = models.ForeignKey(MediaAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name="timelines")
    sort_order = models.PositiveSmallIntegerField(_("sort order"), default=0)

    class Meta:
        ordering = ["sort_order", "step_number"]
        verbose_name = _("timeline step")
        verbose_name_plural = _("timeline steps")

"""
News App — Models
=================
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import UUIDSoftDeleteModel, TimeStampedModel


class NewsCategory(TimeStampedModel):
    name = models.CharField(_("name"), max_length=100, unique=True)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("news category")
        verbose_name_plural = _("news categories")

    def __str__(self) -> str:
        return self.name


class NewsArticle(UUIDSoftDeleteModel):
    """Press releases and announcements."""
    
    title = models.CharField(_("title"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=220, unique=True)
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.TextField(_("summary"), blank=True)
    content = models.TextField(_("content"))
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)
    is_published = models.BooleanField(_("published"), default=False)
    cover_image_id = models.CharField(_("cover image ID"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("news article")
        verbose_name_plural = _("news articles")
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return self.title


class Document(TimeStampedModel):
    """Circulars, PDFs, Brochures."""
    
    title = models.CharField(_("title"), max_length=200)
    file_url = models.URLField(_("file URL"))
    is_public = models.BooleanField(_("public"), default=True)

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

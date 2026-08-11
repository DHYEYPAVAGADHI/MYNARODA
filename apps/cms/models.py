"""
CMS App — Models and Context Processors
=========================================
Content management for the landing page — editable via admin panel.
Also provides site-wide settings injected into every template context.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel


class SiteSettings(TimeStampedModel):
    """
    Singleton model for site-wide configurable settings.
    Only one instance should ever exist (enforced at the admin/service layer).
    """

    # Campaign stats (can be overridden manually or auto-updated by Celery)
    trees_planted = models.PositiveIntegerField(_("trees planted"), default=0)
    volunteers_count = models.PositiveIntegerField(_("volunteers count"), default=0)
    events_count = models.PositiveIntegerField(_("events count"), default=0)
    photos_count = models.PositiveIntegerField(_("photos count"), default=0)

    # Popup Configuration
    popup_enabled = models.BooleanField(_("popup enabled"), default=True)
    popup_delay_seconds = models.PositiveIntegerField(_("popup delay (seconds)"), default=5)
    campaign_title = models.CharField(_("campaign title"), max_length=200, default="Registration for Tree Plantation & Adoption Pledge")
    registration_dates = models.CharField(_("registration dates"), max_length=100, default="1–7 August")
    max_trees_per_registrant = models.PositiveIntegerField(_("max trees per registrant"), default=10)
    popup_message = models.TextField(_("popup message"), default="Join the Green Naroda • Clean Naroda Mission and contribute towards planting 28,855 trees for India's 80th Independence Year.")
    
    class PopupFrequency(models.TextChoices):
        SESSION = "SESSION", _("Once per session")
        ALWAYS = "ALWAYS", _("On every visit")
        
    popup_frequency = models.CharField(
        _("popup frequency"), 
        max_length=20, 
        choices=PopupFrequency.choices, 
        default=PopupFrequency.SESSION
    )

    # Editable text content
    # Editable text content
    hero_tagline = models.CharField(
        _("hero tagline"),
        max_length=200,
        default="28,855 Days of Independence. 28,855 Trees for Tomorrow.",
    )

    # Social links
    facebook_url = models.URLField(_("Facebook URL"), blank=True, default="")
    instagram_url = models.URLField(_("Instagram URL"), blank=True, default="")
    twitter_url = models.URLField(_("Twitter/X URL"), blank=True, default="")
    youtube_url = models.URLField(_("YouTube URL"), blank=True, default="")

    # Contact
    contact_email = models.EmailField(_("contact email"), default="prathampriority@mynaroda.in")
    contact_phone = models.CharField(_("contact phone"), max_length=15, blank=True, default="")

    class Meta:
        verbose_name = _("site settings")
        verbose_name_plural = _("site settings")

    def __str__(self) -> str:
        return "Site Settings"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from django.core.cache import cache
        cache.delete("cms:site_settings")


class Testimonial(TimeStampedModel):
    """Volunteer/citizen testimonials displayed on the landing page."""

    name = models.CharField(_("name"), max_length=100)
    role = models.CharField(
        _("role"),
        max_length=100,
        default="Volunteer",
        help_text=_("e.g. 'Tree Plantation Volunteer' or 'Naroda Resident'"),
    )
    quote = models.TextField(_("quote"), max_length=500, default="")
    avatar_cloudinary_id = models.CharField(
        _("avatar Cloudinary ID"),
        max_length=255,
        blank=True,
        default="",
    )
    is_active = models.BooleanField(_("active"), default=True)
    sort_order = models.PositiveSmallIntegerField(_("sort order"), default=0)

    class Meta:
        verbose_name = _("testimonial")
        verbose_name_plural = _("testimonials")
        ordering = ["sort_order", "-created_at"]

    def __str__(self) -> str:
        return f"{self.name} — {self.role}"


class Partner(TimeStampedModel):
    """Partner/sponsor organisations shown in the partners carousel."""

    name = models.CharField(_("name"), max_length=150)
    logo_cloudinary_id = models.CharField(_("logo Cloudinary ID"), max_length=255)
    website_url = models.URLField(_("website"), blank=True, default="")
    is_active = models.BooleanField(_("active"), default=True)
    sort_order = models.PositiveSmallIntegerField(_("sort order"), default=0)

    class Meta:
        verbose_name = _("partner")
        verbose_name_plural = _("partners")
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name





class ContactMessage(TimeStampedModel):
    """Stores contact submissions from citizens."""

    name = models.CharField(_("full name"), max_length=150)
    email = models.EmailField(_("email address"))
    subject = models.CharField(_("subject"), max_length=200)
    message = models.TextField(_("message"))
    is_resolved = models.BooleanField(_("resolved"), default=False)

    class Meta:
        verbose_name = _("contact message")
        verbose_name_plural = _("contact messages")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} - {self.subject}"


# ─── Dynamic CMS Models ───────────────────────────────────────────────────────

from .models_media import *
from .models_pages import *

class Homepage(TimeStampedModel):
    """Singleton for Homepage content"""
    hero_title = models.CharField(_("hero title"), max_length=150, default="CELEBRATING INDIA'S 80TH INDEPENDENCE YEAR")
    hero_subtitle = models.CharField(_("hero subtitle"), max_length=200, default="PLANTING 28,855 TREES")
    hero_description = models.TextField(_("hero description"), blank=True)
    hero_background = models.ForeignKey(
        MediaAsset, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="homepage_hero", verbose_name=_("hero background")
    )
    
    # Mission Cards
    green_card_title = models.CharField(_("green card title"), max_length=100, default="Green Naroda")
    green_card_text = models.TextField(_("green card description"), blank=True)
    green_card_image = models.ForeignKey(
        MediaAsset, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="homepage_green_card", verbose_name=_("green card image")
    )

    clean_card_title = models.CharField(_("clean card title"), max_length=100, default="Clean Naroda")
    clean_card_text = models.TextField(_("clean card description"), blank=True)
    clean_card_image = models.ForeignKey(
        MediaAsset, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="homepage_clean_card", verbose_name=_("clean card image")
    )
    
    class Meta:
        verbose_name = _("homepage content")
        verbose_name_plural = _("homepage content")

    def __str__(self):
        return "Homepage Content"
        
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class HeroSlide(TimeStampedModel):
    """Cinematic slides for the Homepage Hero Section"""
    
    class MissionType(models.TextChoices):
        GREEN = "GREEN", _("Green Mission")
        CLEAN = "CLEAN", _("Clean Mission")

    homepage = models.ForeignKey(Homepage, on_delete=models.CASCADE, related_name="hero_slides")
    
    title = models.CharField(_("title"), max_length=150)
    subtitle = models.CharField(_("subtitle"), max_length=150, blank=True)
    description = models.TextField(_("description"), blank=True)
    
    image = models.ForeignKey(
        MediaAsset, on_delete=models.CASCADE, related_name="hero_slides",
        verbose_name=_("image"), null=True
    )
    
    mission_type = models.CharField(
        _("mission type"), max_length=20, choices=MissionType.choices, default=MissionType.GREEN
    )
    
    primary_button_text = models.CharField(_("button 1 text"), max_length=50, blank=True)
    primary_button_url = models.CharField(_("button 1 URL"), max_length=200, blank=True)
    
    secondary_button_text = models.CharField(_("button 2 text"), max_length=50, blank=True)
    secondary_button_url = models.CharField(_("button 2 URL"), max_length=200, blank=True)
    
    is_active = models.BooleanField(_("is active"), default=True)
    sort_order = models.PositiveIntegerField(_("display order"), default=0)
    
    class Meta:
        verbose_name = _("hero slide")
        verbose_name_plural = _("hero slides")
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return self.title


class CampaignProgress(TimeStampedModel):
    """Singleton for Campaign Progress (Total targets)"""
    target_trees = models.PositiveIntegerField(_("target trees"), default=28855)
    trees_planted = models.PositiveIntegerField(_("trees planted"), default=0)
    citizens_joined = models.PositiveIntegerField(_("citizens joined"), default=0)
    wards_covered = models.PositiveIntegerField(_("wards covered"), default=14)
    co2_saved_kg = models.PositiveIntegerField(_("CO2 saved (kg)"), default=0)
    
    class Meta:
        verbose_name = _("campaign progress")
        verbose_name_plural = _("campaign progress")

    def __str__(self):
        return "Campaign Progress Target & Stats"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class LeadershipPhotos(TimeStampedModel):
    """Singleton model for holding leadership photos."""
    # Main Planning Committee
    payalben_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    nikunj_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    
    # Co-Conveners
    kiran_raval_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    nirav_joshi_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    gautam_patel_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    vipul_patel_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    jayeshbhai_prajapati_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    chandaben_patel_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    divya_nikunj_khakhi_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)

    # Mentoring Leadership
    nitin_nabin_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    bhupendrabhai_patel_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    jagdish_vishwakarma_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    harshbhai_sanghavi_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    ratnakarji_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    ajay_brahmbhatt_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    anirudhbhai_dave_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    prashantbhai_korat_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    hitendrasinh_chauhan_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    prerakbhai_shah_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    hasmukhbhai_patel_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)
    dineshbhai_makwana_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)

    class Meta:
        verbose_name = _("Leadership Photos")
        verbose_name_plural = _("Leadership Photos")

    def __str__(self):
        return "Leadership Photos (Singleton)"


class BrandingSettings(TimeStampedModel):
    """Singleton model for managing header branding logos."""
    my_naroda_logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    bjp_logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    pratham_logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    gncn_logo = models.ImageField(upload_to="branding/", blank=True, null=True)

    class Meta:
        verbose_name = _("branding settings")
        verbose_name_plural = _("branding settings")

    def __str__(self):
        return "Branding Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        from django.core.cache import cache
        cache.delete("cms:branding_settings")

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class HarGharTirangaRegistration(models.Model):
    """Model for Har Ghar Tiranga campaign registrations."""
    token_id = models.CharField(_("token ID"), max_length=50, unique=True, null=True, blank=True)
    name = models.CharField(_("full name"), max_length=200)
    mobile_number = models.CharField(_("mobile number"), max_length=15)
    address = models.TextField(_("address"))
    latitude = models.FloatField(_("latitude"), null=True, blank=True)
    longitude = models.FloatField(_("longitude"), null=True, blank=True)
    location_text = models.CharField(_("location text"), max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Har Ghar Tiranga registration")
        verbose_name_plural = _("Har Ghar Tiranga registrations")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.mobile_number}"

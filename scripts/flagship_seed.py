import os
import sys
import urllib.request
from django.core.files.base import ContentFile
from django.utils import timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
import django
django.setup()

from apps.accounts.models import User, UserRole
from apps.cms.models import SiteSettings, FAQ, Homepage, HeroSlide, MediaAsset
from apps.news.models import NewsArticle, NewsCategory

def download_image(url, filename):
    print(f"Downloading {filename}...")
    try:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response:
            return ContentFile(response.read(), name=filename)
    except Exception as e:
        print(f"Failed to download {filename}: {e}")
        return None

def seed_flagship():
    print("Seeding Flagship Data...")

    # 1. Admin User
    admin_email = "info@mynaroda.in"
    if not User.objects.filter(email=admin_email).exists():
        admin = User.objects.create_superuser(
            email=admin_email,
            password="Nikunj@1432",
            full_name="Admin User",
            is_active=True,
            is_staff=True,
            is_superuser=True,
            role=UserRole.CITIZEN
        )
        print("Created admin user info@mynaroda.in")

    # 2. Homepage & Hero Slides
    hp, _ = Homepage.objects.get_or_create(pk=1)
    hp.hero_title_en = "Together for a Greener Tomorrow"
    hp.hero_subtitle_en = "Join the Green Naroda, Clean Naroda mission to plant 28,855 trees and build a cleaner, healthier, and more sustainable Ahmedabad."
    hp.save()

    HeroSlide.objects.all().delete()
    
    hero_slides_data = [
        ("Citizens planting trees in Naroda", "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=1920&q=80"),
        ("Children watering saplings", "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?auto=format&fit=crop&w=1920&q=80"),
        ("Women participating in plantation drive", "https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&w=1920&q=80"),
        ("AMC cleanliness workers sweeping streets", "https://images.unsplash.com/photo-1618477461853-cf6ed80fbea5?auto=format&fit=crop&w=1920&q=80"),
        ("Community waste segregation activity", "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&w=1920&q=80"),
        ("Urban park and green boulevard in Ahmedabad", "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?auto=format&fit=crop&w=1920&q=80"),
    ]

    for i, (title, img_url) in enumerate(hero_slides_data):
        img_file = download_image(img_url, f"hero_{i}.jpg")
        asset = MediaAsset.objects.create(
            title=title,
            image=img_file,
            alt_text=title
        )
        HeroSlide.objects.create(
            homepage=hp,
            title_en=title,
            image=asset,
            primary_button_text_en="Take the Pledge",
            primary_button_url="#registration",
            secondary_button_text_en="Track Progress",
            secondary_button_url="#progress",
            is_active=True,
            sort_order=i
        )
    print("Seeded 6 Hero Slides")

    # 3. 10 FAQs
    FAQ.objects.all().delete()
    faqs_data = [
        ("What is the Green Naroda • Clean Naroda Mission?", "It is an official civic mission to plant 28,855 trees to commemorate India's 80th Independence Year."),
        ("Why exactly 28,855 trees?", "The number represents the approximate days of India's independence before completing 80 years by August 2027."),
        ("How can I participate?", "You can participate by taking a pledge online and registering as a volunteer or citizen adopter."),
        ("Do I have to pay to adopt a tree?", "No, tree adoption is completely free. We just need your commitment to nurture it."),
        ("What happens after I register?", "You will receive a Government-verified Certificate of Participation and instructions on upcoming plantation drives."),
        ("Where will the trees be planted?", "Trees will be planted across various wards, parks, canal roads, and designated green zones in Naroda."),
        ("Who is managing this initiative?", "The initiative is supported by local civic bodies, NGOs, and the community of Naroda."),
        ("Can my school or organization join?", "Yes! Organizations can join as partners and organize mass plantation drives."),
        ("What species of trees are planted?", "We focus on native species like Neem, Peepal, Banyan, and Mango that thrive in our local climate."),
        ("How is the progress tracked?", "Progress is tracked via our digital dashboard, where volunteers upload geo-tagged photos of tree growth.")
    ]
    for i, (q, a) in enumerate(faqs_data):
        FAQ.objects.create(question_en=q, answer_en=a, sort_order=i, is_active=True)
    print("Seeded 10 FAQs")

    # 4. 6 News Articles
    NewsArticle.objects.all().delete()
    cat, _ = NewsCategory.objects.get_or_create(name="Updates")
    news_titles = [
        "Mass Plantation Drive",
        "Cleanliness Awareness Rally",
        "School Participation Program",
        "Women Green Initiative",
        "Ward-wise Progress Report",
        "Independence Day Green Campaign"
    ]
    for i, title in enumerate(news_titles):
        NewsArticle.objects.create(
            title_en=title,
            slug=f"news-{i}",
            category=cat,
            summary_en=f"Join us for the {title} happening this month.",
            content_en=f"Full details of the {title} event. We are excited to see massive participation from the citizens of Naroda.",
            published_at=timezone.now(),
            is_published=True
        )
    print("Seeded 6 News Articles")

    print("Flagship Seeding Complete!")

if __name__ == "__main__":
    seed_flagship()

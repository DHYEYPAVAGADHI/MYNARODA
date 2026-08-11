import os
import sys
import random
import datetime
import django
from django.utils import timezone

# Setup django environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from apps.accounts.models import User, UserRole, VolunteerLevel
from apps.trees.models import Tree, TreeSpecies, VerificationStatus, TreeHealth, GrowthStage, TreePhoto
from apps.events.models import Event, EventRegistration
from apps.gallery.models import Photo, GalleryCategory, GalleryCollection
from apps.news.models import NewsArticle, NewsCategory, Document
from apps.cms.models import SiteSettings, Testimonial, Partner, FAQ
from apps.certificates.models import Certificate
from apps.notifications.models import Notification

def seed():
    print("Clearing old data...")
    # Clean up tables
    Notification.objects.all().delete()
    Certificate.objects.all().delete()
    EventRegistration.objects.all().delete()
    Event.objects.all().delete()
    TreePhoto.objects.all().delete()
    Tree.objects.all().delete()
    TreeSpecies.objects.all().delete()
    Photo.objects.all().delete()
    GalleryCollection.objects.all().delete()
    GalleryCategory.objects.all().delete()
    NewsArticle.objects.all().delete()
    NewsCategory.objects.all().delete()
    Document.objects.all().delete()
    Testimonial.objects.all().delete()
    Partner.objects.all().delete()
    FAQ.objects.all().delete()
    
    # Do not delete all users to avoid losing admin user, just delete non-staff
    User.objects.filter(is_staff=False).delete()

    print("Seeding new campaign data...")

    # 1. Seeding SiteSettings
    site_settings = SiteSettings.objects.create(
        trees_planted=105,
        volunteers_count=52,
        events_count=10,
        photos_count=30,
        hero_tagline_en="28,855 Days of Independence. 28,855 Trees for Tomorrow.",
        hero_tagline_gu="સ્વતંત્રતાના ૨૮,૮૫૫ દિવસ. આવતીકાલ માટે ૨૮,૮૫૫ વૃક્ષ.",
        hero_tagline_hi="स्वतंत्रता के 28,855 दिन। कल के लिए 28,855 पेड़।",
        contact_email="hello@mynaroda.in",
        contact_phone="+91791234567"
    )

    # 2. Seeding Testimonials
    testimonials = [
        ("Rahul Patel", "Volunteer", "Planting a Neem tree in Naroda was a way to connect back to the roots of our community. Seeing it grow is incredible!", "નરોડામાં લીમડાનું વૃક્ષ વાવવું એ આપણા સમુદાયના મૂળિયાં સાથે જોડાવાનો માર્ગ હતો.", "नरोदा में नीम का पेड़ लगाना हमारे समुदाय की जड़ों से जुड़ने का एक तरीका था।"),
        ("Sita Shah", "Citizen", "A wonderful initiative for India's 80th Independence. Every ward is turning greener. Highly recommend joining as a volunteer.", "ભારતની ૮૦મી સ્વતંત્રતા માટે એક અદ્ભુત પહેલ. દરેક વોર્ડ હરિયાળો બની રહ્યો છે.", "भारत की 80वीं स्वतंत्रता के लिए एक अद्भुत पहल। हर वार्ड हरा-भरा हो रहा है।"),
        ("Amit Verma", "Coordinator", "We verify coordinates and care instructions for every logged sapling to ensure survival rates exceed 90%.", "આપણે વાવેલા દરેક રોપાના કોઓર્ડિનેટ્સ અને સંભાળની સૂચનાઓ ચકાસીએ છીએ.", "हम यह सुनिश्चित करने के लिए प्रत्येक रोपे गए पौधे के निर्देशांक और देखभाल निर्देशों की पुष्टि करते हैं।"),
    ]
    for idx, (name, role, q_en, q_gu, q_hi) in enumerate(testimonials):
        Testimonial.objects.create(
            name=name,
            role=role,
            quote_en=q_en,
            quote_gu=q_gu,
            quote_hi=q_hi,
            sort_order=idx
        )

    # 3. Seeding FAQs
    faqs = [
        ("What is the 28,855 Trees campaign?", "It commemorates India's 80th Independence Day by planting one tree for every single day of independence.", "તે સ્વતંત્રતાના દરેક દિવસ માટે એક વૃક્ષ વાવીને ભારતની ૮૦મી સ્વતંત્રતા દિવસની ઉજવણી કરે છે.", "यह स्वतंत्रता के प्रत्येक दिन के लिए एक पेड़ लगाकर भारत के 80वें स्वतंत्रता दिवस का जश्न मनाता है।"),
        ("How can I register my tree?", "Log in to your dashboard, navigate to 'Plant Tree', input GPS coordinates and upload a photo.", "તમારા ડેશબોર્ડમાં લોગિન કરો, 'વૃક્ષ વાવો' પર જાઓ અને જીપીએસ કોઓર્ડિનેટ્સ દાખલ કરો.", "अपने डैशबोर्ड में लॉग इन करें, 'पेड़ लगाएं' पर जाएं, जीपीएस निर्देशांक दर्ज करें और फोटो अपलोड करें।"),
        ("Who verifies the trees?", "Campaign ward coordinators visit the tree location to verify the species, health, and log growth stages.", "તમામ રોપાઓની આરોગ્ય ચકાસણી વોર્ડ કોઓર્ડિનેટર્સ દ્વારા કરવામાં આવે છે.", "सभी रोपों का स्वास्थ्य परीक्षण वार्ड समन्वयकों द्वारा किया जाता है।")
    ]
    for idx, (q, a, q_gu, a_gu) in enumerate(faqs):
        FAQ.objects.create(
            question_en=q,
            answer_en=a,
            question_gu=q_gu,
            answer_gu=a_gu,
            sort_order=idx
        )

    # 4. Seeding Partners
    partners = ["Gujarat Forest Department", "Ahmedabad Municipal Corporation", "Adani Foundation", "Rotary Club Naroda"]
    for idx, name in enumerate(partners):
        Partner.objects.create(
            name=name,
            logo_cloudinary_id="partner_logo_mock",
            is_active=True,
            sort_order=idx
        )

    # 5. Seeding Tree Species
    species_data = [
        ("Neem", "Azadirachta indica", "Fast-growing evergreen tree, known for therapeutic properties and air purification.", True),
        ("Peepal", "Ficus religiosa", "Provides round-the-clock oxygen, highly sacred tree.", True),
        ("Banyan", "Ficus benghalensis", "National tree of India, creates large canopy shade.", True),
        ("Mango", "Mangifera indica", "Produces delicious fruit, thrives well in local climate.", True),
        ("Gulmohar", "Delonix regia", "Known for its flamboyant display of orange-red flowers.", False)
    ]
    species_objs = []
    for name, sci_name, desc, native in species_data:
        sp = TreeSpecies.objects.create(
            name=name,
            scientific_name=sci_name,
            description=desc,
            native_to_gujarat=native,
            image_cloudinary_id="species_mock"
        )
        species_objs.append(sp)

    # 6. Seeding News
    news_categories = ["Announcements", "Press Releases", "Circulars"]
    cat_objs = [NewsCategory.objects.create(name=c, slug=c.lower().replace(" ", "-")) for c in news_categories]
    
    NewsArticle.objects.create(
        title="Green Naroda Campaign Officially Launched by Forest Department",
        slug="green-naroda-campaign-officially-launched",
        category=cat_objs[0],
        summary="Official launch of 28,855 trees drive celebrating India's 80th Independence Day.",
        content="Today marked the official inauguration of the Green Naroda plantation drive. Handed over by local ward officers, over 500 saplings were planted in the first phase. The drive runs until Independence Day, August 15, 2027.",
        published_at=timezone.now(),
        is_published=True
    )

    NewsArticle.objects.create(
        title="Ward 4 achieves 5,000 trees milestone",
        slug="ward-4-achieves-milestone",
        category=cat_objs[1],
        summary="Naroda East Ward 4 becomes the first region to cross 5,000 registered verified plantings.",
        content="Residents and local school groups in Ward 4 have set a new record by successfully planting and verifying 5,000 native trees including Banyan, Neem, and Peepal. The ward committee thanked all active student coordinators.",
        published_at=timezone.now(),
        is_published=True
    )

    Document.objects.create(
        title="Ward Plantation Guidelines (PDF)",
        file_url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        is_public=True
    )
    Document.objects.create(
        title="List of Approved Native Species Circular",
        file_url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        is_public=True
    )

    # 7. Seeding Users (Volunteers & Citizens)
    first_names = ["Rajesh", "Aarav", "Pooja", "Vikram", "Sneha", "Rahul", "Vijay", "Divya", "Sanjay", "Kunal", "Meera", "Anil", "Sunita", "Deepak", "Jyoti", "Harish", "Neha", "Rohan", "Geeta", "Manish"]
    last_names = ["Patel", "Shah", "Sharma", "Joshi", "Verma", "Mehta", "Vyas", "Trivedi", "Rathod", "Solanki", "Gohil", "Parmar", "Chauhan", "Dave", "Pandya"]
    
    volunteer_users = []
    for i in range(50):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        full_name = f"{fname} {lname}"
        email = f"{fname.lower()}.{lname.lower()}{i}@example.com"
        
        user = User.objects.create(
            email=email,
            full_name=full_name,
            role=UserRole.VOLUNTEER if i < 35 else UserRole.CITIZEN,
            volunteer_level=random.choice(VolunteerLevel.choices)[0],
            total_hours=random.randint(5, 80),
            trees_planted=random.randint(1, 20),
            is_active=True,
            is_phone_verified=True,
            phone=f"+9198765{i:05d}"
        )
        user.set_password("naroda2027")
        user.save()
        if user.role == UserRole.VOLUNTEER:
            volunteer_users.append(user)

    # 8. Seeding Events
    events_data = [
        ("Naroda Canal Road Afforestation Drive", "canal-road-drive", Event.EventType.PLANTATION),
        ("Ward 4 Parks Canopy Clean-up & Seed Sowing", "ward-4-parks-drive", Event.EventType.CLEANUP),
        ("Independence Day Eve Mega Plantation", "independence-day-eve-drive", Event.EventType.PLANTATION),
        ("Naroda School Awareness Lecture & Demonstration", "school-awareness-demo", Event.EventType.AWARENESS)
    ]
    event_objs = []
    for title, slug, etype in events_data:
        ev = Event.objects.create(
            title=title,
            slug=slug,
            event_type=etype,
            description=f"Join the local community drive for {title}. Saplings and tools will be provided by the Forest Department. Please bring water bottles.",
            location_name="Naroda, Ahmedabad",
            latitude=23.0722,
            longitude=72.6582,
            starts_at=timezone.now() + datetime.timedelta(days=random.randint(2, 30)),
            ends_at=timezone.now() + datetime.timedelta(days=random.randint(2, 30)) + datetime.timedelta(hours=3),
            max_volunteers=100,
            is_published=True,
            status=Event.EventStatus.UPCOMING,
            trees_target=150
        )
        event_objs.append(ev)

    # 9. Seeding Event Registrations
    for ev in event_objs:
        # Register a few volunteers
        regs = random.sample(volunteer_users, k=15)
        for r in regs:
            EventRegistration.objects.create(
                event=ev,
                user=r,
                is_cancelled=False,
                attended=False,
                trees_planted=0
            )

    # 10. Seeding Trees
    locations_ward = [
        ("Naroda GIDC Sector 1", "Ward 1"),
        ("Muthiya Village Park", "Ward 2"),
        ("Canal Road East Side", "Ward 3"),
        ("Naroda Gam Lake Garden", "Ward 4"),
        ("Haridarshan Cross Roads", "Ward 5")
    ]
    
    # Naroda approximate bounds: lat 23.06 to 23.09, lng 72.63 to 72.67
    for i in range(100):
        sp = random.choice(species_objs)
        planter = random.choice(volunteer_users)
        loc_name, ward = random.choice(locations_ward)
        
        # Jitter coordinates slightly
        lat = 23.065 + random.random() * 0.02
        lng = 72.635 + random.random() * 0.03
        
        tree = Tree.objects.create(
            species=sp,
            contributor=planter,
            planted_by=planter,
            latitude=lat,
            longitude=lng,
            location_name=f"{loc_name} Area {i+1}",
            ward=ward,
            notes="Healthy sapling in rich organic soil.",
            planted_at=timezone.now().date() - datetime.timedelta(days=random.randint(0, 100)),
            verification_status=random.choice(VerificationStatus.choices)[0],
            health_status=random.choice(TreeHealth.choices)[0],
            growth_stage=random.choice(GrowthStage.choices)[0],
            qr_code_url=f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://mynaroda.in/trees/{planter.id}/"
        )
        
        # Add a growth photo for each tree
        TreePhoto.objects.create(
            tree=tree,
            cloudinary_id=f"seed_photo_{tree.id}",
            cloudinary_url="https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=600&q=80",
            is_primary=True,
            caption="Plantation photo logged successfully.",
            uploaded_by=planter
        )

    # 11. Seeding Gallery Photos
    gallery_categories = ["Plantation Drives", "Volunteers", "Nature", "Community Achievements"]
    gal_cats = [GalleryCategory.objects.create(name=c, slug=c.lower().replace(" ", "-")) for c in gallery_categories]
    
    photo_urls = [
        "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=800&q=80"
    ]

    for i in range(30):
        gc = random.choice(gal_cats)
        user = random.choice(volunteer_users)
        Photo.objects.create(
            title=f"Plantation Drive Highlight {i+1}",
            cloudinary_id=f"drive_pic_{i}",
            url=random.choice(photo_urls),
            thumbnail_url=random.choice(photo_urls),
            webp_url=random.choice(photo_urls),
            category=gc,
            photographer=user,
            approval_status=Photo.ApprovalStatus.APPROVED,
            is_featured=True if i < 8 else False,
            location="Naroda Ward Region"
        )

    # 12. Seeding Certificates
    for i in range(10):
        v = volunteer_users[i]
        Certificate.objects.create(
            user=v,
            certificate_type=Certificate.CertificateType.VOLUNTEER,
        )

    # 13. Seeding Notifications
    for v in volunteer_users[:15]:
        Notification.objects.create(
            user=v,
            notification_type=Notification.NotificationType.SUCCESS,
            title="Tree Verified Successfully",
            message="Your logged Neem tree has been verified by the ward coordinator. View your certificate!",
            link="/certificates/"
        )

    print("Success! Seeding completed successfully.")

if __name__ == "__main__":
    seed()

from apps.cms.models import PageMission, PageObjective, PageHighlight, PageActivity, PageStatistic, PageTimeline

def run():
    print("Seeding Green Naroda CMS Page...")
    green, created = PageMission.objects.get_or_create(
        slug="green-naroda",
        defaults={
            "title": "Green Naroda",
            "hero_title": "GREEN NARODA",
            "hero_subtitle": "Official Tree Plantation Mission",
            "hero_description": "Join the historic movement to plant 28,855 trees across Naroda, celebrating 28,855 days of India's independence. A Government of Gujarat initiative for a greener tomorrow.",
            "intro_title": "Mission Introduction",
            "intro_text_1": "The Green Naroda initiative is a massive environmental campaign sanctioned by the Government of Gujarat. It aims to significantly expand the urban canopy by strategically planting 28,855 indigenous trees across all municipal wards of Naroda.",
            "intro_text_2": "This mission goes beyond mere plantation; it emphasizes the 'Adoption Pledge', ensuring that every sapling planted is nurtured by a registered citizen or volunteer organization until it matures into a self-sustaining tree.",
            "vision_title": "The Vision",
            "vision_text": "To transform Naroda into the greenest urban district in Gujarat by fostering a powerful synergy between government infrastructure and citizen participation. We envision a sustainable ecosystem where urban development coexists harmoniously with robust green cover.",
        }
    )
    if created:
        PageObjective.objects.create(page=green, title="Urban Canopy Expansion", description="Systematically increasing the green cover across all 14 wards by planting native, high-oxygen-yielding tree species.")
        PageObjective.objects.create(page=green, title="Citizen Stewardship", description="Ensuring high survival rates through mandatory adoption pledges where citizens take ownership of tree maintenance.")
        PageObjective.objects.create(page=green, title="Biodiversity Restoration", description="Creating micro-forests in urban spaces to restore local bird and insect populations native to the Gujarat region.")
        PageObjective.objects.create(page=green, title="Air Quality Improvement", description="Targeting heavily congested traffic zones to act as natural carbon sinks and significantly reduce particulate pollution.")

    print("Seeding Clean Naroda CMS Page...")
    clean, created = PageMission.objects.get_or_create(
        slug="clean-naroda",
        defaults={
            "title": "Clean Naroda",
            "hero_title": "CLEAN NARODA",
            "hero_subtitle": "Official Cleanliness Mission",
            "hero_description": "Together towards a cleaner and healthier Naroda. Fostering a community-driven movement focusing on waste segregation, street hygiene, and civic responsibility.",
            "intro_title": "Mission Introduction",
            "intro_text_1": "Cleanliness is a fundamental civic right and a collective responsibility. The Clean Naroda mission represents the Government's stringent approach toward solid waste management, sanitation, and public hygiene.",
            "intro_text_2": "Our methodology focuses on aggressive waste segregation at the source, daily community sweeping drives, and total eradication of single-use plastics across market areas, ensuring a disease-free environment.",
            "vision_title": "The Vision",
            "vision_text": "A zero-waste municipal zone where every street, park, and public gathering area is maintained immaculately by a coalition of dedicated sanitation workers and vigilant local residents.",
        }
    )
    if created:
        PageObjective.objects.create(page=clean, title="Waste Segregation", description="Mandating source-level division of wet, dry, and hazardous medical waste for proper disposal.")
        PageObjective.objects.create(page=clean, title="Plastic Free Areas", description="Strictly prohibiting single-use plastics in main markets and commercial hubs.")
        PageObjective.objects.create(page=clean, title="Community Ownership", description="Empowering resident welfare associations to maintain and monitor cleanliness in their zones.")
        PageObjective.objects.create(page=clean, title="Daily Road Sweeping", description="Ensuring massive daily cleaning drives on arterial roads using mechanical sweepers and staff.")
    
    print("Seeding successful.")

if __name__ == '__main__':
    run()

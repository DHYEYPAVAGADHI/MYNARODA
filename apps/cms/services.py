import logging
from decimal import Decimal
from django.core.cache import cache

from apps.volunteers.models import PledgeRegistration
from apps.cms.models import HarGharTirangaRegistration, CampaignStatistics
from apps.student_portal.models import StudentSubmission
from apps.competitions.models import CompetitionRegistration

logger = logging.getLogger(__name__)

def get_dashboard_stats():
    """
    Returns the live dashboard statistics safely aggregated from the database.
    Caches the result for 60 seconds to avoid heavy load on the homepage.
    Returns 0/default values gracefully on any database errors to prevent 500 crashes.
    """
    cache_key = 'live_dashboard_stats'
    stats = cache.get(cache_key)
    
    if stats:
        return stats

    try:
        # Aggregations
        pledge_count = PledgeRegistration.objects.count()
        tiranga_count = HarGharTirangaRegistration.objects.count()
        student_count = StudentSubmission.objects.count()
        org_count = CompetitionRegistration.objects.filter(status='APPROVED').count()

        # Complex calculations
        trees_planted = pledge_count + tiranga_count + student_count + org_count
        citizens_joined = pledge_count + tiranga_count + student_count
        
        # Manual stats
        db_stats = CampaignStatistics.objects.first()
        cleanliness_drives = db_stats.cleanliness_drives if db_stats else 212
        waste_removed_tons = db_stats.waste_removed_tons if db_stats else Decimal('64.0')

        # Target math
        target = 28855
        raw_progress = (trees_planted / target) * 100 if target > 0 else 0
        progress_percent = min(round(raw_progress), 100)
        
        stats = {
            'trees_planted': trees_planted,
            'citizens_joined': citizens_joined,
            'organizations': org_count,
            'students': student_count,
            'cleanliness_drives': cleanliness_drives,
            'waste_removed_tons': float(waste_removed_tons),
            'progress_percent': progress_percent,
            'tiranga_distribution_count': tiranga_count,
        }
        
        # Cache for 60 seconds
        cache.set(cache_key, stats, 60)
        return stats

    except Exception as e:
        logger.error(f"Failed to fetch live dashboard stats: {str(e)}")
        # Safe fallback
        return {
            'trees_planted': 0,
            'citizens_joined': 0,
            'organizations': 0,
            'students': 0,
            'cleanliness_drives': 212,
            'waste_removed_tons': 64.0,
            'progress_percent': 0,
            'tiranga_distribution_count': 0,
        }

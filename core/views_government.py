from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Cattle, Insemination, BirthRecord, Alert, TreatmentRecord, VaccinationRecord, Farm
from .serializers import (
    CattleSerializer, InseminationSerializer, BirthRecordSerializer,
    AlertSerializer, TreatmentRecordSerializer, VaccinationRecordSerializer,
    FarmSerializer
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_national_farm_stats(request):
    """
    Get national-level farm statistics:
    - Total number of registered farms
    - Total number of cattle
    - Regional distribution of farms
    """
    if request.user.role != 'government':
        return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

    # Get all farms
    farms = Farm.objects.all()
    
    # Get statistics
    total_farms = farms.count()
    total_cattle = Cattle.objects.count()
    
    # Get regional distribution
    regional_stats = farms.values('region').annotate(
        farm_count=Count('id'),
        cattle_count=Count('cattle', distinct=True)
    )

    return Response({
        "total_farms": total_farms,
        "total_cattle": total_cattle,
        "regional_stats": list(regional_stats),
        "last_updated": timezone.now()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_national_health_stats(request):
    """
    Get national-level health statistics:
    - Active health alerts
    - Treatment records
    - Vaccination coverage
    """
    if request.user.role != 'government':
        return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

    # Get active health alerts
    alerts = Alert.objects.filter(is_read=False)
    active_alerts = alerts.count()
    
    # Get treatment records from last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    treatments = TreatmentRecord.objects.filter(created_at__gte=thirty_days_ago)
    treatment_count = treatments.count()
    
    # Get vaccination coverage
    total_cattle = Cattle.objects.count()
    vaccinated_cattle = Cattle.objects.filter(
        vaccinations__isnull=False
    ).distinct().count()

    return Response({
        "active_alerts": active_alerts,
        "recent_treatments": treatment_count,
        "vaccination_coverage": {
            "total": total_cattle,
            "vaccinated": vaccinated_cattle,
            "coverage_percentage": (vaccinated_cattle / total_cattle * 100) if total_cattle > 0 else 0
        },
        "last_updated": timezone.now()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_national_reproduction_stats(request):
    """
    Get national-level reproduction statistics:
    - Insemination success rates
    - Birth records
    - Pregnancy rates
    """
    if request.user.role != 'government':
        return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

    # Get statistics for last 90 days
    ninety_days_ago = timezone.now() - timedelta(days=90)
    
    # Insemination stats
    inseminations = Insemination.objects.filter(created_at__gte=ninety_days_ago)
    total_inseminations = inseminations.count()
    successful_inseminations = inseminations.filter(is_confirmed_positive=True).count()
    
    # Birth stats
    births = BirthRecord.objects.filter(created_at__gte=ninety_days_ago)
    total_births = births.count()
    
    return Response({
        "insemination_stats": {
            "total": total_inseminations,
            "successful": successful_inseminations,
            "success_rate": (successful_inseminations / total_inseminations * 100) if total_inseminations > 0 else 0
        },
        "birth_stats": {
            "total": total_births,
            "last_90_days": births.count()
        },
        "last_updated": timezone.now()
    })

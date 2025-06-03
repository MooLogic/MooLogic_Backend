from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Milk_record
from core.models import Cattle, Farm

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_national_milk_production(request):
    """
    Get national-level milk production statistics:
    - Total production
    - Regional distribution
    - Production trends
    """
    if request.user.role != 'government':
        return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

    # Get statistics for last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Total production
    total_production = Milk_record.objects.filter(
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # Regional production
    regional_production = Milk_record.objects.filter(
        created_at__gte=thirty_days_ago
    ).values('cattle_tag__farm__region').annotate(
        total=Sum('quantity'),
        farms=Count('cattle_tag__farm', distinct=True),
        cattle=Count('cattle_tag', distinct=True)
    )
    
    # Production trend (weekly)
    production_trend = []
    current_date = timezone.now()
    for week in range(4):  # Last 4 weeks
        start_date = current_date - timedelta(days=7*(week+1))
        end_date = current_date - timedelta(days=7*week)
        weekly_production = Milk_record.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        production_trend.append({
            "week_start": start_date.strftime('%Y-%m-%d'),
            "week_end": end_date.strftime('%Y-%m-%d'),
            "production": weekly_production
        })
    
    return Response({
        "total_production": total_production,
        "regional_production": list(regional_production),
        "production_trend": production_trend,
        "last_updated": timezone.now()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_national_milking_stats(request):
    """
    Get national-level milking statistics:
    - Active milking cattle
    - Milking frequency
    - Average production
    """
    if request.user.role != 'government':
        return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

    # Get active milking cattle
    active_cattle = Cattle.objects.filter(
        is_active=True,
        is_lactating=True
    )
    
    # Milking frequency statistics
    milking_records = Milk_record.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).values('cattle_tag__id').annotate(
        count=Count('id'),
        avg_production=Sum('quantity') / Count('id')
    )
    
    return Response({
        "milking_stats": {
            "total_active_cattle": active_cattle.count(),
            "avg_milkings_per_day": milking_records.count() / 7,
            "avg_production_per_cow": milking_records.aggregate(
                avg=Sum('avg_production') / Count('id')
            )['avg'] or 0
        },
        "last_updated": timezone.now()
    })

from datetime import timedelta
from django.shortcuts import render
from django.core.exceptions import ValidationError
from .models import Milk_record
from .serializers import Milk_recordSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Q
from core.models import Cattle
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    responses={200: openapi.Response('Milk records', schema=Milk_recordSerializer(many=True).data if False else None)}
)
def milk_records(request):
    """
    List all milk records for the user's farm.
    """
    if request.method == 'GET':
        milk_records = Milk_record.objects.filter(
            cattle_tag__farm=request.user.farm
        ).select_related('cattle_tag')
        serializer = Milk_recordSerializer(milk_records, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    manual_parameters=[openapi.Parameter('cattle_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Cattle ID')],
    responses={200: Milk_recordSerializer(many=True)}
)
def milk_production_by_cattle(request, cattle_id):
    """
    Get milk production by cattle id.
    """
    try:
        cattle = Cattle.objects.get(
            id=cattle_id,
            farm=request.user.farm
        )
    except Cattle.DoesNotExist:
        return Response(
            {"error": "Cattle not found or not in your farm"},
            status=status.HTTP_404_NOT_FOUND
        )

    milk_records = Milk_record.objects.filter(cattle_tag=cattle)
    serializer = Milk_recordSerializer(milk_records, many=True)
    return Response(serializer.data)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    request_body=Milk_recordSerializer,
    responses={201: Milk_recordSerializer}
)
def add_milk_record(request):
    """
    Add a new milk record.
    """
    try:
        # Get the cattle
        cattle = Cattle.objects.get(
            ear_tag_no=request.data['cattle_tag'],
            farm=request.user.farm
        )

        # Create the record data
        data = {
            'cattle_tag': cattle.id,
            'quantity': request.data['quantity'],
            'shift': request.data['shift'],
            'ear_tag_no': request.data['cattle_tag'],
            'date': request.data['date'],
            'time': request.data['time']
        }

        # Create and save the record
        serializer = Milk_recordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Milk record added successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "error": "Invalid data",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Cattle.DoesNotExist:
        return Response(
            {"error": "Cattle not found or not in your farm"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred",
            "details": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    responses={200: openapi.Response('Missing records list')}
)
def check_missing_records(request):
    """
    Check for missing milk records in the user's farm.
    """
    alerts = Milk_record.check_missing_records(request.user.farm)
    return Response({
        "missing_records": alerts,
        "count": len(alerts)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    manual_parameters=[openapi.Parameter('cattle_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Cattle ID')],
    responses={200: openapi.Response('Milking schedule')}
)
def get_cattle_milking_schedule(request, cattle_id):
    """
    Get the milking schedule for a specific cattle.
    """
    try:
        cattle = Cattle.objects.get(
            id=cattle_id,
            farm=request.user.farm
        )
        return Response({
            "schedule": cattle.get_milking_schedule(),
            "frequency": cattle.milking_frequency,
            "avg_daily_production": float(cattle.avg_daily_milk),
            "next_milking": cattle.get_next_milking_time()
        })
    except Cattle.DoesNotExist:
        return Response(
            {"error": "Cattle not found or not in your farm"},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    manual_parameters=[openapi.Parameter('cattle_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Cattle ID')],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'milking_frequency': openapi.Schema(type=openapi.TYPE_STRING),
            'custom_milking_times': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: openapi.Response('Updated milking settings')}
)
def update_cattle_milking_settings(request, cattle_id):
    """
    Update milking settings for a specific cattle.
    """
    try:
        cattle = Cattle.objects.get(
            id=cattle_id,
            farm=request.user.farm
        )
        
        if 'milking_frequency' in request.data:
            cattle.milking_frequency = request.data['milking_frequency']
        
        if 'custom_milking_times' in request.data:
            cattle.custom_milking_times = request.data['custom_milking_times']
        
        cattle.save()
        
        return Response({
            "message": "Milking settings updated successfully",
            "schedule": cattle.get_milking_schedule(),
            "frequency": cattle.milking_frequency
        })
    except Cattle.DoesNotExist:
        return Response(
            {"error": "Cattle not found or not in your farm"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

#function to update milk records
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    manual_parameters=[openapi.Parameter('record_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Milk record ID')],
    request_body=Milk_recordSerializer,
    responses={200: Milk_recordSerializer}
)
def update_milk_record(request, record_id):
    """
    Update a milk record.
    """
    try:
        milk_record = Milk_record.objects.get(id=record_id)
    except Milk_record.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = Milk_recordSerializer(milk_record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view
@permission_classes([IsAuthenticated])
def get_milk_production(cattle_id, days):
    """
    Get milk production grouped by date for the last `days` days.
    """
    start_date = timezone.now().date() - timedelta(days=days)
    milk_records = (
        Milk_record.objects
        .filter(cattle_tag=cattle_id, date__gte=start_date)
        .values('date')  # Group by date
        .annotate(total_production=Sum('quantity'))  # Sum milk production per day
        .order_by('-date')
    )
    
    return milk_records


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    manual_parameters=[openapi.Parameter('cattle_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Cattle ID')],
    responses={200: Milk_recordSerializer(many=True)}
)
def milk_production_by_cattle_last_7_days(request, cattle_id):
    return Response(get_milk_production(cattle_id, 7))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    manual_parameters=[openapi.Parameter('cattle_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Cattle ID')],
    responses={200: Milk_recordSerializer(many=True)}
)
def milk_production_by_cattle_last_30_days(request, cattle_id):
    return Response(get_milk_production(cattle_id, 30))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    manual_parameters=[openapi.Parameter('cattle_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Cattle ID')],
    responses={200: Milk_recordSerializer(many=True)}
)
def milk_production_by_cattle_last_90_days(request, cattle_id):
    return Response(get_milk_production(cattle_id, 90))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    manual_parameters=[openapi.Parameter('cattle_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Cattle ID')],
    responses={200: Milk_recordSerializer(many=True)}
)
def milk_production_by_cattle_last_300_days(request, cattle_id):
    return Response(get_milk_production(cattle_id, 300))


# Functions for overall farm production
def get_farm_milk_production(days):
    """
    Get milk production grouped by date for the last `days` days.
    """
    start_date = timezone.now().date() - timedelta(days=days)
    milk_records = (
        Milk_record.objects
        .filter(date__gte=start_date)
        .values('date')  # Group by date
        .annotate(total_production=Sum('quantity'))  # Sum milk production per day
        .order_by('-date')
    )
    return milk_records

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    responses={200: openapi.Response('Farm production records')}
)
def farm_production_last_7_days(request):
    records = get_farm_milk_production(7)
    return Response(records)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    responses={200: openapi.Response('Farm production records')}
)
def farm_production_last_30_days(request):
    records = get_farm_milk_production(30)
    return Response(records)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    responses={200: openapi.Response('Farm production records')}
)
def farm_production_last_90_days(request):
    records = get_farm_milk_production(90)
    return Response(records)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    responses={200: openapi.Response('Lactating cattle list')}
)
def get_lactating_cattle(request):
    """
    Get all lactating cattle from the current farm.
    A cow is considered lactating if:
    1. It's a female cow
    2. It's not in 'dry_off' status
    3. It has calved at least once (has last_calving_date)
    """
    try:
        # Get all potential lactating cattle
        cattle = Cattle.objects.filter(
            farm=request.user.farm,
            gender='female',
            life_stage='cow'
        ).exclude(
            gestation_status='dry_off'
        ).filter(
            last_calving_date__isnull=False
        ).select_related('farm')
        
        # For each cattle, get their current milking frequency and last milking time
        cattle_data = []
        current_time = timezone.now()
        
        for cow in cattle:
            # Get lactation status
            lactation_info = cow.get_lactation_status()
            
            # Skip if not in lactating state
            if lactation_info['status'] not in ['lactating', 'colostrum']:
                continue
            
            # Get last milk record
            last_record = Milk_record.objects.filter(
                cattle_tag=cow
            ).order_by('-date', '-time').first()
            
            # Convert milking frequency from string to number
            frequency_map = {'once': 1, 'twice': 2, 'thrice': 3}
            milking_frequency = frequency_map.get(cow.milking_frequency, 2)  # default to twice if invalid
            
            data = {
                'id': cow.id,
                'ear_tag_no': cow.ear_tag_no,
                'name': f"{cow.breed or 'Unknown Breed'} - {cow.ear_tag_no}",
                'milking_frequency': milking_frequency,
                'last_milking': last_record.created_at if last_record else None,
                'can_milk_now': True,  # Default to True, will be updated below
                'days_in_milk': lactation_info['days_in_milk'],
                'lactation_number': lactation_info['lactation_number']
            }
            
            if last_record and last_record.created_at:
                # Calculate if enough time has passed since last milking based on frequency
                time_diff = current_time - last_record.created_at
                hours_since_last_milking = time_diff.total_seconds() / 3600
                min_hours_between_milking = 24 / milking_frequency
                data['can_milk_now'] = hours_since_last_milking >= min_hours_between_milking
            
            cattle_data.append(data)
            
        return Response({
            "count": len(cattle_data),
            "results": cattle_data
        })
    except Exception as e:
        import traceback
        print(f"Error in get_lactating_cattle: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return Response(
            {"error": f"Failed to fetch lactating cattle: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    responses={200: openapi.Response("Today's production stats")}
)
def get_today_production_stats(request):
    """
    Get milk production statistics for today including:
    - Total production
    - Number of records
    - Active milking cattle
    """
    try:
        today = timezone.now().date()
        
        # Get today's records
        today_records = Milk_record.objects.filter(
            cattle_tag__farm=request.user.farm,
            date=today
        )
        
        # Calculate total production
        total_production = today_records.aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        # Get active milking cattle count
        active_cattle = Cattle.objects.filter(
            farm=request.user.farm,
            gender='female',
            life_stage='cow'
        ).exclude(
            gestation_status='dry_off'
        ).filter(
            last_calving_date__isnull=False
        ).count()
        
        return Response({
            'total_production': float(total_production),
            'records_count': today_records.count(),
            'active_milking_cattle': active_cattle
        })
    except Exception as e:
        print(f"Error in get_today_production_stats: {str(e)}")
        return Response(
            {"error": f"Failed to fetch today's production stats: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
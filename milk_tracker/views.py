from datetime import timedelta
from django.shortcuts import render

from .models import Milk_record
from .serializers import Milk_recordSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from django.db.models import Sum
from core.models import Cattle

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def milk_records(request):
    """
    List all milk records.
    """
    if request.method == 'GET':
        milk_records = Milk_record.objects.all()
        serializer = Milk_recordSerializer(milk_records, many=True)
        return Response(serializer.data)
##function to get milk production by cattle id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def milk_production_by_cattle(request, cattle_id):
    """
    Get milk production by cattle id.
    """
    if request.method == 'GET':
        milk_records = Milk_record.objects.filter(cattle_tag=cattle_id)
        serializer = Milk_recordSerializer(milk_records, many=True)
        return Response(serializer.data)
    
# function to add new milk records
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_milk_record(request):
    """
    Add a new milk record.
    """
    if request.method == 'POST':
        
        cattle = Cattle.objects.filter(ear_tag_no=request.data['cattle_tag']).first()
        print(cattle.id)

       
        data = {
            'cattle_tag': cattle.id,
            'quantity': request.data['quantity'],
            'shift': request.data['shift'],
            'ear_tag_no': request.data['cattle_tag'],
            
        }
        #if a record with day today and shift already exists, return an error
        if Milk_record.objects.filter(date=now().date(), shift=request.data['shift']).exists():
            return Response({"error": "Record for today and this shift already exists."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = Milk_recordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # If the serializer is not valid, return the errors
            print(request.data)
            print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)

#function to update milk records
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
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
    start_date = now().date() - timedelta(days=days)
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
def milk_production_by_cattle_last_7_days(request, cattle_id):
    return Response(get_milk_production(cattle_id, 7))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def milk_production_by_cattle_last_30_days(request, cattle_id):
    return Response(get_milk_production(cattle_id, 30))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def milk_production_by_cattle_last_90_days(request, cattle_id):
    return Response(get_milk_production(cattle_id, 90))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def milk_production_by_cattle_last_300_days(request, cattle_id):
    return Response(get_milk_production(cattle_id, 300))


# Functions for overall farm production
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_farm_milk_production(days):
    """
    Get milk production grouped by date for the last `days` days.
    """
    start_date = now().date() - timedelta(days=days)
    milk_records = (
        Milk_record.objects
        .filter( date__gte=start_date)
        .values('date')  # Group by date
        .annotate(total_production=Sum('quantity'))  # Sum milk production per day
        .order_by('-date')
    )
    return milk_records
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def farm_production_last_7_days(request):
    return Response(get_farm_milk_production(7))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def farm_production_last_30_days(request):
    return Response(get_farm_milk_production( 30))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def farm_production_last_90_days(request):
    return Response(get_farm_milk_production(90))
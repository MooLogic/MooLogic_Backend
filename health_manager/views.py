from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import TreatmentRecord, VaccinationRecord, PeriodicVaccinationRecord
from .serializers import TreatmentRecordSerializer, VaccinationRecordSerializer, PeriodicVaccinationRecordSerializer

# CRUD for TreatmentRecord
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_treatment_record(request):
    serializer = TreatmentRecordSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_treatment_records(request):
    records = TreatmentRecord.objects.all()
    serializer = TreatmentRecordSerializer(records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_treatment_record_by_id(request, record_id):
    record = get_object_or_404(TreatmentRecord, id=record_id)
    serializer = TreatmentRecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_treatment_record(request, record_id):
    record = get_object_or_404(TreatmentRecord, id=record_id)
    serializer = TreatmentRecordSerializer(record, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_treatment_record(request, record_id):
    record = get_object_or_404(TreatmentRecord, id=record_id)
    record.delete()
    return Response({'message': 'Treatment record deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

# CRUD for VaccinationRecord
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vaccination_record(request):
    serializer = VaccinationRecordSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_vaccination_records(request):
    records = VaccinationRecord.objects.all()
    serializer = VaccinationRecordSerializer(records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_vaccination_record_by_id(request, record_id):
    record = get_object_or_404(VaccinationRecord, id=record_id)
    serializer = VaccinationRecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_vaccination_record(request, record_id):
    record = get_object_or_404(VaccinationRecord, id=record_id)
    serializer = VaccinationRecordSerializer(record, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_vaccination_record(request, record_id):
    record = get_object_or_404(VaccinationRecord, id=record_id)
    record.delete()
    return Response({'message': 'Vaccination record deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

# CRUD for PeriodicVaccinationRecord
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_periodic_vaccination_record(request):
    data = request.data.copy()
    # Calculate next vaccination date if not provided
    if 'next_vaccination_date' not in data and 'last_vaccination_date' in data and 'interval_days' in data:
        last_vaccination_date = datetime.strptime(data['last_vaccination_date'], "%Y-%m-%d").date()
        interval_days = int(data['interval_days'])
        data['next_vaccination_date'] = last_vaccination_date + timedelta(days=interval_days)
    
    serializer = PeriodicVaccinationRecordSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_periodic_vaccination_record(request, record_id):
    record = get_object_or_404(PeriodicVaccinationRecord, id=record_id)
    data = request.data.copy()
    # Recalculate next vaccination date if last_vaccination_date or interval_days is updated
    if 'last_vaccination_date' in data or 'interval_days' in data:
        last_vaccination_date = datetime.strptime(data.get('last_vaccination_date', record.last_vaccination_date.strftime("%Y-%m-%d")), "%Y-%m-%d").date()
        interval_days = int(data.get('interval_days', record.interval_days))
        data['next_vaccination_date'] = last_vaccination_date + timedelta(days=interval_days)
    
    serializer = PeriodicVaccinationRecordSerializer(record, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_periodic_vaccination_records(request):
    records = PeriodicVaccinationRecord.objects.all()
    serializer = PeriodicVaccinationRecordSerializer(records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_periodic_vaccination_record_by_id(request, record_id):
    record = get_object_or_404(PeriodicVaccinationRecord, id=record_id)
    serializer = PeriodicVaccinationRecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_periodic_vaccination_record(request, record_id):
    record = get_object_or_404(PeriodicVaccinationRecord, id=record_id)
    record.delete()
    return Response({'message': 'Periodic vaccination record deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
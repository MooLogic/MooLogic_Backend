from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from .models import Cattle, Insemination, BirthRecord, Alert, Farm, TreatmentRecord, VaccinationRecord, PeriodicVaccinationRecord, PeriodicTreatmentRecord, GestationMilestone, GestationCheck
from .serializers import (
    CattleSerializer, InseminationSerializer, BirthRecordSerializer, AlertSerializer,
    FarmSerializer, TreatmentRecordSerializer, VaccinationRecordSerializer,
    PeriodicVaccinationRecordSerializer, PeriodicTreatmentRecordSerializer,
    GestationDataSerializer, GestationCheckSerializer, GestationMilestoneSerializer
)
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_cattle(request):
    cattle = Cattle.objects.filter(farm=request.user.farm)
    serializer = CattleSerializer(cattle, many=True, context={'request': request})
    return Response({"count": cattle.count(), "results": serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pregnant_cattle(request):
    try:
        # Debug logging
        print("User farm:", request.user.farm)
        
        # Get cattle that are either pregnant or near calving
        cattle = Cattle.objects.filter(
            farm=request.user.farm,
            gestation_status__in=['pregnant', 'calving']
        ).order_by('expected_calving_date')
        
        # Debug logging
        print(f"Found {cattle.count()} pregnant/calving cattle")
        for cow in cattle:
            print(f"Cattle ID: {cow.id}, Tag: {cow.ear_tag_no}, Status: {cow.gestation_status}, Due: {cow.expected_calving_date}")
        
        serializer = CattleSerializer(cattle, many=True, context={'request': request})
        data = {"count": cattle.count(), "results": serializer.data}
        print("Response data:", data)
        return Response(data)
    except Exception as e:
        print(f"Error in list_pregnant_cattle: {str(e)}")
        return Response(
            {"error": "Failed to fetch pregnant cattle"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_gestation_data(request):
    """
    Get comprehensive gestation data for all pregnant cattle in the farm.
    Includes gestation progress, milestones, health checks, and Gantt chart data.
    """
    try:
        # Get all pregnant/calving cattle
        cattle = Cattle.objects.filter(
            farm=request.user.farm,
            gestation_status__in=['pregnant', 'calving']
        ).prefetch_related(
            'gestation_milestones',
            'gestation_checks',
            'treatment_records',
            'vaccination_records',
            'periodic_treatment_records',
            'periodic_vaccination_records',
            'alerts'
        ).order_by('expected_calving_date')

        # Prepare data for each cattle
        gestation_data = []
        for cow in cattle:
            data = {
                'cattle': cow,
                'treatment_records': cow.treatment_records.all(),
                'vaccination_records': cow.vaccination_records.all(),
                'periodic_treatment_records': cow.periodic_treatment_records.all(),
                'periodic_vaccination_records': cow.periodic_vaccination_records.all(),
                'alerts': cow.alerts.filter(read=False)
            }
            gestation_data.append(data)

        # Serialize the data with request context
        serializer = GestationDataSerializer(gestation_data, many=True, context={'request': request})
        return Response({
            "count": len(gestation_data),
            "results": serializer.data
        })
    except Exception as e:
        print(f"Error in list_gestation_data: {str(e)}")
        return Response(
            {"error": "Failed to fetch gestation data"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cattle_by_id(request, pk):
    try:
        cattle = Cattle.objects.get(pk=pk, farm=request.user.farm)
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = CattleSerializer(cattle, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_cattle(request):
    """
    Create a new cattle record.
    The farm is automatically set to the user's farm.
    """
    try:
        # Add the farm to the request data
        data = request.data.copy()
        data['farm'] = request.user.farm.id
        
        serializer = CattleSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            new_cattle = serializer.save()
                
            # Generate initial alerts if needed
            alerts = new_cattle.generate_alerts()
            
            response_data = serializer.data
            if alerts:
                response_data['alerts'] = alerts
            
            return Response(response_data, status=status.HTTP_201_CREATED)
    
        return Response(
            {
                "error": "Invalid data provided",
                "details": serializer.errors
            }, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {
                "error": "Failed to create cattle",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cattle(request, pk):
    try:
        cattle = Cattle.objects.get(pk=pk, farm=request.user.farm)
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = CattleSerializer(cattle, data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cattle(request, pk):
    try:
        cattle = Cattle.objects.get(pk=pk, farm=request.user.farm)
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    cattle.delete()
    return Response({'message': 'Cattle deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_cattle_alerts(request, cattle_id):
    try:
        cattle = Cattle.objects.get(pk=cattle_id, farm=request.user.farm)
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    alerts = cattle.generate_alerts()
    for alert in alerts:
        Alert.objects.create(
            cattle=cattle,
            message=alert['message'],
            due_date=alert['due_date'],
            priority=alert['priority']
        )
    serializer = AlertSerializer(Alert.objects.filter(cattle=cattle, is_read=False), many=True)
    return Response({'alerts': serializer.data})

# TreatmentRecord Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_treatment_record(request):
    data = request.data.copy()
    try:
        cattle = Cattle.objects.get(pk=data['cattle'], farm=request.user.farm)
        data['veterinarian'] = request.user.id
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = TreatmentRecordSerializer(data=data)
    if serializer.is_valid():
        treatment = serializer.save()
        Alert.objects.create(
            cattle=cattle,
            message=f"Treatment '{treatment.treatment_name}' administered to {cattle.ear_tag_no} on {treatment.treatment_date}.",
            due_date=timezone.now().date(),
            priority='Low'
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_treatment_records(request):
    try:
        records = TreatmentRecord.objects.filter(cattle__farm=request.user.farm)
        print(f"Found {records.count()} treatment records")  # Debug log
        serializer = TreatmentRecordSerializer(records, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching treatment records: {str(e)}")  # Debug log
        return Response(
            {"error": "Failed to fetch treatment records"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_treatment_record_by_id(request, pk):
    record = get_object_or_404(TreatmentRecord, pk=pk, cattle__farm=request.user.farm)
    serializer = TreatmentRecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_treatment_record(request, pk):
    record = get_object_or_404(TreatmentRecord, pk=pk, cattle__farm=request.user.farm)
    serializer = TreatmentRecordSerializer(record, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_treatment_record(request, pk):
    record = get_object_or_404(TreatmentRecord, pk=pk, cattle__farm=request.user.farm)
    record.delete()
    return Response({'message': 'Treatment record deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# VaccinationRecord Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vaccination_record(request):
    data = request.data.copy()
    try:
        cattle = Cattle.objects.get(pk=data['cattle'], farm=request.user.farm)
        data['veterinarian'] = request.user.id
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = VaccinationRecordSerializer(data=data)
    if serializer.is_valid():
        vaccination = serializer.save()
        Alert.objects.create(
            cattle=cattle,
            message=f"Vaccination '{vaccination.vaccination_name}' administered to {cattle.ear_tag_no} on {vaccination.vaccination_date}.",
            due_date=timezone.now().date(),
            priority='Low'
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_vaccination_records(request):
    try:
        records = VaccinationRecord.objects.filter(cattle__farm=request.user.farm)
        print(f"Found {records.count()} vaccination records")  # Debug log
        serializer = VaccinationRecordSerializer(records, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching vaccination records: {str(e)}")  # Debug log
        return Response(
            {"error": "Failed to fetch vaccination records"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vaccination_record_by_id(request, pk):
    record = get_object_or_404(VaccinationRecord, pk=pk, cattle__farm=request.user.farm)
    serializer = VaccinationRecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_vaccination_record(request, pk):
    record = get_object_or_404(VaccinationRecord, pk=pk, cattle__farm=request.user.farm)
    serializer = VaccinationRecordSerializer(record, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_vaccination_record(request, pk):
    record = get_object_or_404(VaccinationRecord, pk=pk, cattle__farm=request.user.farm)
    record.delete()
    return Response({'message': 'Vaccination record deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# PeriodicVaccinationRecord Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_periodic_vaccination_record(request):
    data = request.data.copy()
    try:
        if not data.get('is_farm_wide'):
            cattle = Cattle.objects.get(pk=data['cattle'], farm=request.user.farm)
            data['veterinarian'] = request.user.id
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)

    if 'next_vaccination_date' not in data and 'last_vaccination_date' in data and 'interval_days' in data:
        last_vaccination_date = datetime.strptime(data['last_vaccination_date'], "%Y-%m-%d").date()
        interval_days = int(data['interval_days'])
        data['next_vaccination_date'] = last_vaccination_date + timedelta(days=interval_days)

    serializer = PeriodicVaccinationRecordSerializer(data=data)
    if serializer.is_valid():
        record = serializer.save()
        if record.is_due_for_vaccination():
            if record.is_farm_wide:
                # Create alerts for all cattle in the farm
                for cattle in Cattle.objects.filter(farm=request.user.farm):
                    Alert.objects.create(
                        cattle=cattle,
                        message=f"Farm-wide periodic vaccination '{record.vaccination_name}' due on {record.next_vaccination_date}.",
                        due_date=record.next_vaccination_date,
                        priority='High'
                    )
            else:
                Alert.objects.create(
                    cattle=cattle,
                    message=f"Periodic vaccination '{record.vaccination_name}' due for {cattle.ear_tag_no} on {record.next_vaccination_date}.",
                    due_date=record.next_vaccination_date,
                    priority='High'
                )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_periodic_vaccination_records(request):
    cattle_id = request.query_params.get('cattle')
    if cattle_id:
        records = PeriodicVaccinationRecord.objects.filter(
            Q(cattle__id=cattle_id, cattle__farm=request.user.farm) |
            Q(is_farm_wide=True, veterinarian__farm=request.user.farm)
        )
    else:
        records = PeriodicVaccinationRecord.objects.filter(
            Q(cattle__farm=request.user.farm) |
            Q(is_farm_wide=True, veterinarian__farm=request.user.farm)
        ).distinct()
    serializer = PeriodicVaccinationRecordSerializer(records, many=True)
    return Response({'results': serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_periodic_vaccination_record_by_id(request, pk):
    record = get_object_or_404(PeriodicVaccinationRecord, pk=pk, cattle__farm=request.user.farm)
    serializer = PeriodicVaccinationRecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_periodic_vaccination_record(request, pk):
    record = get_object_or_404(PeriodicVaccinationRecord, pk=pk, cattle__farm=request.user.farm)
    data = request.data.copy()
    if 'last_vaccination_date' in data or 'interval_days' in data:
        last_vaccination_date = datetime.strptime(
            data.get('last_vaccination_date', record.last_vaccination_date.strftime("%Y-%m-%d")),
            "%Y-%m-%d"
        ).date()
        interval_days = int(data.get('interval_days', record.interval_days))
        data['next_vaccination_date'] = last_vaccination_date + timedelta(days=interval_days)

    serializer = PeriodicVaccinationRecordSerializer(record, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_periodic_vaccination_record(request, pk):
    record = get_object_or_404(PeriodicVaccinationRecord, pk=pk, cattle__farm=request.user.farm)
    record.delete()
    return Response({'message': 'Periodic vaccination record deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# PeriodicTreatmentRecord Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_periodic_treatment_record(request):
    data = request.data.copy()
    try:
        if not data.get('is_farm_wide'):
            cattle = Cattle.objects.get(pk=data['cattle'], farm=request.user.farm)
            data['veterinarian'] = request.user.id
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)

    if 'next_treatment_date' not in data and 'last_treatment_date' in data and 'interval_days' in data:
        last_treatment_date = datetime.strptime(data['last_treatment_date'], "%Y-%m-%d").date()
        interval_days = int(data['interval_days'])
        data['next_treatment_date'] = last_treatment_date + timedelta(days=interval_days)

    serializer = PeriodicTreatmentRecordSerializer(data=data)
    if serializer.is_valid():
        record = serializer.save()
        if record.is_due_for_treatment():
            if record.is_farm_wide:
                # Create alerts for all cattle in the farm
                for cattle in Cattle.objects.filter(farm=request.user.farm):
                    Alert.objects.create(
                        cattle=cattle,
                        message=f"Farm-wide periodic treatment '{record.treatment_name}' due on {record.next_treatment_date}.",
                        due_date=record.next_treatment_date,
                        priority='High'
                    )
            else:
                Alert.objects.create(
                    cattle=cattle,
                    message=f"Periodic treatment '{record.treatment_name}' due for {cattle.ear_tag_no} on {record.next_treatment_date}.",
                    due_date=record.next_treatment_date,
                    priority='High'
                )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_periodic_treatment_records(request):
    cattle_id = request.query_params.get('cattle')
    if cattle_id:
        records = PeriodicTreatmentRecord.objects.filter(
            Q(cattle__id=cattle_id, cattle__farm=request.user.farm) |
            Q(is_farm_wide=True, veterinarian__farm=request.user.farm)
        )
    else:
        records = PeriodicTreatmentRecord.objects.filter(
            Q(cattle__farm=request.user.farm) |
            Q(is_farm_wide=True, veterinarian__farm=request.user.farm)
        ).distinct()
    serializer = PeriodicTreatmentRecordSerializer(records, many=True)
    return Response({'results': serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_periodic_treatment_record_by_id(request, pk):
    record = get_object_or_404(PeriodicTreatmentRecord, pk=pk, cattle__farm=request.user.farm)
    serializer = PeriodicTreatmentRecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_periodic_treatment_record(request, pk):
    record = get_object_or_404(PeriodicTreatmentRecord, pk=pk, cattle__farm=request.user.farm)
    data = request.data.copy()
    if 'last_treatment_date' in data or 'interval_days' in data:
        last_treatment_date = datetime.strptime(
            data.get('last_treatment_date', record.last_treatment_date.strftime("%Y-%m-%d")),
            "%Y-%m-%d"
        ).date()
        interval_days = int(data.get('interval_days', record.interval_days))
        data['next_treatment_date'] = last_treatment_date + timedelta(days=interval_days)

    serializer = PeriodicTreatmentRecordSerializer(record, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_periodic_treatment_record(request, pk):
    record = get_object_or_404(PeriodicTreatmentRecord, pk=pk, cattle__farm=request.user.farm)
    record.delete()
    return Response({'message': 'Periodic treatment record deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# Insemination Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_inseminations(request):
    inseminations = Insemination.objects.filter(cattle__farm=request.user.farm)
    serializer = InseminationSerializer(inseminations, many=True)
    return Response({"count": inseminations.count(), "results": serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_insemination(request):
    try:
        # Log the incoming request data for debugging
        print("Received insemination data:", request.data)
        
        # Validate required fields
        if not request.data.get('cattle'):
            return Response({'error': 'Cattle ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('insemination_date'):
            return Response({'error': 'Insemination date is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('insemination_method'):
            return Response({'error': 'Insemination method is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cattle = Cattle.objects.get(pk=request.data['cattle'], farm=request.user.farm)
        except Cattle.DoesNotExist:
            return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if cattle is appropriate for insemination
        if cattle.gender != 'female':
            return Response(
                {'error': 'Only female cattle can be inseminated'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if cattle.life_stage == 'calf':
            return Response(
                {'error': 'Cannot inseminate a calf'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if cattle.gestation_status == 'pregnant':
            return Response(
                {'error': 'Cannot inseminate a pregnant cattle'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if enough time has passed since last calving (60 days minimum)
        if cattle.last_calving_date:
            days_since_calving = (timezone.now().date() - cattle.last_calving_date).days
            if days_since_calving < 60:
                return Response(
                    {'error': f'Must wait at least 60 days after calving. {60 - days_since_calving} days remaining.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = InseminationSerializer(data=request.data)
        if serializer.is_valid():
            insemination = serializer.save(cattle=cattle)
            
            # Create pregnancy check alert
            insemination.create_pregnancy_check_alert()
            
            # Create calving preparation alert if pregnancy is confirmed
            if insemination.pregnancy_check_status == 'confirmed':
                Alert.objects.create(
                    cattle=cattle,
                    message=f"Prepare for calving - Expected date: {insemination.expected_calving_date}",
                    due_date=insemination.expected_calving_date - timedelta(days=14),
                    priority='High',
                    alert_type='general'
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Log validation errors for debugging
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        # Log unexpected errors
        print("Error creating insemination:", str(e))
        return Response(
            {'error': f'Failed to create insemination record: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def send_alert_email(user, subject, message, priority):
    """Utility function to send alert emails"""
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Loonko Alert: {subject}</h2>
                <div style="margin: 20px 0; padding: 15px; border-radius: 5px; background-color: {
                    '#fee2e2' if priority == 'High' else '#fef3c7' if priority == 'Medium' else '#f3f4f6'
                };">
                    <p style="margin: 0; color: {
                        '#dc2626' if priority == 'High' else '#d97706' if priority == 'Medium' else '#374151'
                    };">
                        Priority: {priority}
                    </p>
                    <p>{message}</p>
                </div>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #6b7280; font-size: 0.875rem;">This is an automated message from Loonko Farm Management System.</p>
            </div>
        </body>
    </html>
    """
    
    # Plain text version
    plain_message = f"""
    Loonko Alert: {subject}
    Priority: {priority}

    {message}

    This is an automated message from Loonko Farm Management System.
    """
    
    try:
        result = send_mail(
            subject=f"Loonko Alert: {subject}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        return result > 0  # Return True if email was sent successfully
    except Exception as e:
        print(f"Failed to send email alert: {str(e)}")
        return False

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_insemination(request, pk):
    try:
        insemination = Insemination.objects.get(pk=pk, cattle__farm=request.user.farm)
    except Insemination.DoesNotExist:
        return Response({'error': 'Insemination record not found'}, status=status.HTTP_404_NOT_FOUND)

    # Store old status for comparison
    old_status = insemination.pregnancy_check_status
    
    # Validate pregnancy check date if provided
    if request.data.get('pregnancy_check_date'):
        try:
            # Try to parse date in DD-MM-YYYY format
            check_date = datetime.strptime(request.data['pregnancy_check_date'], "%d-%m-%Y").date()
            if check_date < insemination.insemination_date:
                return Response(
                    {'error': 'Pregnancy check date cannot be before insemination date'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            # If parsing fails, let the serializer handle the validation
            pass

    # Add detailed logging for debugging
    print(f"Request data: {request.data}")
    print(f"Insemination instance: {insemination.__dict__}")
    
    serializer = InseminationSerializer(insemination, data=request.data, partial=True)
    if serializer.is_valid():
        print("Serializer is valid")
        print(f"Validated data: {serializer.validated_data}")
        print(f"Instance before save: {insemination.__dict__}")
        try:
            updated_insemination = serializer.save()
            print(f"Instance after save: {updated_insemination.__dict__}")
            print(f"Updated status: {updated_insemination.pregnancy_check_status}")
            
            # Return the updated data
            return Response(serializer.data)
        except Exception as e:
            print(f"Error during save: {str(e)}")
            import traceback
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'Save failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        print(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # If pregnancy status changed to confirmed
        if old_status != 'confirmed' and updated_insemination.pregnancy_check_status == 'confirmed':
            print(f"Creating calving alert for cattle {updated_insemination.cattle.ear_tag_no}")
            try:
                calving_alert = Alert.objects.create(
                    cattle=updated_insemination.cattle,
                    title=f"Prepare for calving - Expected date: {updated_insemination.expected_calving_date}",
                    description=f"Calving preparation required for cattle {updated_insemination.cattle.ear_tag_no}",
                    date=timezone.now(),
                    type='reproduction',
                    priority='High'
                )
                print(f"Calving alert created successfully: {calving_alert.id}")
            except Exception as e:
                print(f"Error creating calving alert: {str(e)}")
                import traceback
                print("Traceback:", traceback.format_exc())
                # Continue even if alert creation fails
                
            # Send calving preparation email
            if not send_alert_email(
                user=request.user,
                subject="Calving Preparation Required",
                message=f"Cattle {updated_insemination.cattle.ear_tag_no} is confirmed pregnant. "
                       f"Expected calving date is {updated_insemination.expected_calving_date}. "
                       f"Please start preparation 14 days before the expected date.",
                priority='High'
            ):
                print(f"Failed to send calving preparation email to {request.user.email}")
            
            # Create vaccination reminder
            try:
                vaccination_alert = Alert.objects.create(
                    cattle=updated_insemination.cattle,
                    title=f"Schedule pregnancy vaccination for {updated_insemination.cattle.ear_tag_no}",
                    description=f"Pregnancy vaccination due for cattle {updated_insemination.cattle.ear_tag_no}",
                    date=timezone.now(),
                    type='reproduction',
                    priority='High'
                )
                print(f"Vaccination alert created successfully: {vaccination_alert.id}")
            except Exception as e:
                print(f"Error creating vaccination alert: {str(e)}")
                import traceback
                print("Traceback:", traceback.format_exc())
                # Continue even if alert creation fails
            
            # Send vaccination reminder email
            if not send_alert_email(
                user=request.user,
                subject="Pregnancy Vaccination Required",
                message=f"Please schedule pregnancy vaccination for cattle {updated_insemination.cattle.ear_tag_no} "
                       f"within the next 7 days.",
                priority='High'
            ):
                print(f"Failed to send vaccination reminder email to {request.user.email}")
            
            # Send calving preparation email
            if not send_alert_email(
                user=request.user,
                subject="Calving Preparation Required",
                message=f"Cattle {updated_insemination.cattle.ear_tag_no} is confirmed pregnant. "
                       f"Expected calving date is {updated_insemination.expected_calving_date}. "
                       f"Please start preparation 14 days before the expected date.",
                priority='High'
            ):
                print(f"Failed to send calving preparation email to {request.user.email}")
            
            # Create vaccination reminder
            vaccination_alert = Alert.objects.create(
                cattle=updated_insemination.cattle,
                title=f"Schedule pregnancy vaccination for {updated_insemination.cattle.ear_tag_no}",
                description=f"Pregnancy vaccination due for cattle {updated_insemination.cattle.ear_tag_no}",
                date=timezone.now(),
                type='reproduction',
                priority='High'
            )
            
            # Send vaccination reminder email
            if not send_alert_email(
                user=request.user,
                subject="Pregnancy Vaccination Required",
                message=f"Please schedule pregnancy vaccination for cattle {updated_insemination.cattle.ear_tag_no} "
                       f"within the next 7 days.",
                priority='High'
            ):
                print(f"Failed to send vaccination reminder email to {request.user.email}")
        
        # If pregnancy status changed to negative
        elif old_status != 'negative' and updated_insemination.pregnancy_check_status == 'negative':
            # Create next insemination reminder
            next_insemination_alert = Alert.objects.create(
                cattle=updated_insemination.cattle,
                title="Schedule next insemination - Previous attempt unsuccessful",
                description=f"Next insemination attempt due for cattle {updated_insemination.cattle.ear_tag_no}",
                date=timezone.now(),
                type='reproduction',
                priority='Medium'
            )
            
            # Send next insemination reminder email
            if not send_alert_email(
                user=request.user,
                subject="Schedule Next Insemination",
                message=f"The pregnancy test for cattle {updated_insemination.cattle.ear_tag_no} was negative. "
                       f"Please schedule the next insemination attempt within 21 days.",
                priority='Medium'
            ):
                print(f"Failed to send insemination reminder email to {request.user.email}")
        
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_pregnancy_checks(request):
    """Get all inseminations that need pregnancy confirmation"""
    pending_checks = Insemination.objects.filter(
        cattle__farm=request.user.farm,
        pregnancy_check_status='pending',
        insemination_date__lte=timezone.now().date() - timedelta(days=21)
    )
    serializer = InseminationSerializer(pending_checks, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_insemination(request, pk):
    try:
        insemination = Insemination.objects.get(pk=pk, cattle__farm=request.user.farm)
    except Insemination.DoesNotExist:
        return Response({'error': 'Insemination record not found'}, status=status.HTTP_404_NOT_FOUND)
    insemination.delete()
    return Response({'message': 'Insemination record deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# BirthRecord Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_birth_records(request):
    """List all birth records for the farm"""
    birth_records = BirthRecord.objects.filter(cattle__farm=request.user.farm)
    serializer = BirthRecordSerializer(birth_records, many=True)
    return Response({"count": birth_records.count(), "results": serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_birth_record(request, pk):
    """Get a specific birth record"""
    try:
        birth_record = BirthRecord.objects.get(pk=pk, cattle__farm=request.user.farm)
    except BirthRecord.DoesNotExist:
        return Response({'error': 'Birth record not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = BirthRecordSerializer(birth_record)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_birth_record(request):
    """Create a new birth record with automatic calf registration"""
    try:
        # Validate cattle ownership and pregnancy status
        cattle = Cattle.objects.get(pk=request.data['cattle'], farm=request.user.farm)
        
        # Create birth record
        serializer = BirthRecordSerializer(data=request.data)
        if serializer.is_valid():
            birth_record = serializer.save()
            
            # Get all alerts generated during the birth record creation
            alerts = Alert.objects.filter(
                cattle__in=[birth_record.cattle],
                created_at__gte=birth_record.created_at
            )
            
            # If a calf was registered successfully, include its alerts too
            if birth_record.calving_outcome == 'successful':
                calf_alerts = Alert.objects.filter(
                    cattle__ear_tag_no=birth_record.calf_ear_tag,
                    created_at__gte=birth_record.created_at
                )
                alerts = alerts | calf_alerts
            
            response_data = {
                'birth_record': serializer.data,
                'alerts': AlertSerializer(alerts, many=True).data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
            # except Cattle.DoesNotExist:
            #     return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {'error': f'Failed to create birth record: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_birth_record(request, pk):
    """Update an existing birth record"""
    try:
        birth_record = BirthRecord.objects.get(pk=pk, cattle__farm=request.user.farm)
    except BirthRecord.DoesNotExist:
        return Response({'error': 'Birth record not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = BirthRecordSerializer(birth_record, data=request.data, partial=True)
    if serializer.is_valid():
        updated_record = serializer.save()
        
        # If complications were added, create a new alert
        if (request.data.get('complications') or 
            request.data.get('calving_outcome') in ['complications', 'stillborn', 'died_shortly_after']):
            Alert.objects.create(
                cattle=updated_record.cattle,
                message=f"New complications reported for calving on {updated_record.calving_date}",
                due_date=timezone.now().date(),
                priority='High',
                alert_type='general'
            )
        
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_birth_record(request, pk):
    """Delete a birth record"""
    try:
        birth_record = BirthRecord.objects.get(pk=pk, cattle__farm=request.user.farm)
    except BirthRecord.DoesNotExist:
        return Response({'error': 'Birth record not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Store calf information before deletion
    calf_ear_tags = birth_record.calf_ear_tag.split(',')
    
    # Delete the birth record
    birth_record.delete()
    
    # Also delete the associated calf records if they exist
    for ear_tag in calf_ear_tags:
        try:
            calf = Cattle.objects.get(ear_tag_no=ear_tag.strip())
            calf.delete()
        except Cattle.DoesNotExist:
            continue
    
    return Response(
        {'message': 'Birth record and associated calf records deleted successfully'},
        status=status.HTTP_204_NO_CONTENT
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cattle_birth_history(request, cattle_id):
    """Get birth history for a specific cattle (both as mother and as calf)"""
    try:    
        cattle = Cattle.objects.get(pk=cattle_id, farm=request.user.farm)
        
        # Get records where this cattle is the mother
        as_mother = BirthRecord.objects.filter(cattle=cattle)
        
        # Get this cattle's own birth record (if it exists)
        try:
            own_birth = BirthRecord.objects.get(calf_ear_tag__contains=cattle.ear_tag_no)
            own_birth_data = BirthRecordSerializer(own_birth).data
        except BirthRecord.DoesNotExist:
            own_birth_data = None
        
        response_data = {
            'cattle_info': {
                'ear_tag_no': cattle.ear_tag_no,
                'birth_date': cattle.birth_date,
                'gender': cattle.gender,
            },
            'as_mother': BirthRecordSerializer(as_mother, many=True).data,
            'own_birth_record': own_birth_data
        }
        return Response(response_data)
    
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)

# Alert Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_alerts(request):
    """
    Get all alerts for the user's farm.
    Supports filtering by:
    - type (query param)
    - read status (query param)
    - priority (query param)
    """
    try:
        alerts = Alert.objects.filter(cattle__farm=request.user.farm)

        # Apply filters if provided
        alert_type = request.query_params.get('type')
        if alert_type:
            alerts = alerts.filter(type=alert_type)

        read_status = request.query_params.get('read')
        if read_status is not None:
            is_read = read_status.lower() == 'true'
            alerts = alerts.filter(read=is_read)

        priority = request.query_params.get('priority')
        if priority:
            alerts = alerts.filter(priority=priority)

        # Order by priority (High to Low) and then by date (newest first)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        alerts = sorted(alerts, key=lambda x: (priority_order.get(x.priority.lower(), 3), -x.created_at.timestamp()))

        serializer = AlertSerializer(alerts, many=True)
        return Response({
            "count": len(alerts),
            "results": serializer.data
        })
    except Exception as e:
        print(f"Error in list_alerts: {str(e)}")  # Add debug logging
        return Response(
            {"error": f"Failed to fetch alerts: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_alerts(request):
    """Get all unread alerts for the user's farm."""
    try:
        alerts = Alert.objects.filter(
            cattle__farm=request.user.farm,
            is_read=False
        ).order_by('-created_at')
        
        serializer = AlertSerializer(alerts, many=True)
        return Response({
            "count": alerts.count(),
            "results": serializer.data
        })
    except Exception as e:
        return Response(
            {"error": f"Failed to fetch unread alerts: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_alert_as_read(request, alert_id):
    """Mark a specific alert as read."""
    try:
        alert = get_object_or_404(Alert, id=alert_id, cattle__farm=request.user.farm)
        alert.read = True
        alert.save()
        serializer = AlertSerializer(alert)
        return Response(serializer.data)
    except Exception as e:
        print(f"Error in mark_alert_as_read: {str(e)}")  # Add debug logging
        return Response(
            {"error": f"Failed to mark alert as read: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_alerts_as_read(request):
    """Mark all alerts for the user's farm as read."""
    try:
        Alert.objects.filter(cattle__farm=request.user.farm).update(read=True)
        return Response({"message": "All alerts marked as read"})
    except Exception as e:
        print(f"Error in mark_all_alerts_as_read: {str(e)}")  # Add debug logging
        return Response(
            {"error": f"Failed to mark all alerts as read: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_alert(request, alert_id):
    """Delete a specific alert."""
    try:
        alert = get_object_or_404(Alert, id=alert_id, cattle__farm=request.user.farm)
        alert.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response(
            {"error": f"Failed to delete alert: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Farm Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_farms(request):
    farms = Farm.objects.all()
    serializer = FarmSerializer(farms, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_farm(request):
    serializer = FarmSerializer(data=request.data)
    if serializer.is_valid():
        farm_code = f"FARM{str(Farm.objects.count() + 1).zfill(3)}"
        serializer.validated_data['farm_code'] = farm_code
        farm = serializer.save()
        request.user.farm = farm
        request.user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cattle_health_records(request, cattle_id=None):
    try:
        if cattle_id:
            cattle = Cattle.objects.get(pk=cattle_id, farm=request.user.farm)
            treatments = TreatmentRecord.objects.filter(cattle=cattle)
            vaccinations = VaccinationRecord.objects.filter(cattle=cattle)
            periodic_treatments = PeriodicTreatmentRecord.objects.filter(
                Q(cattle=cattle) |
                Q(is_farm_wide=True, veterinarian__farm=request.user.farm)
            )
            periodic_vaccinations = PeriodicVaccinationRecord.objects.filter(
                Q(cattle=cattle) |
                Q(is_farm_wide=True, veterinarian__farm=request.user.farm)
            )
        else:
            treatments = TreatmentRecord.objects.filter(cattle__farm=request.user.farm)
            vaccinations = VaccinationRecord.objects.filter(cattle__farm=request.user.farm)
            periodic_treatments = PeriodicTreatmentRecord.objects.filter(
                Q(cattle__farm=request.user.farm) |
                Q(is_farm_wide=True, veterinarian__farm=request.user.farm)
            ).distinct()
            periodic_vaccinations = PeriodicVaccinationRecord.objects.filter(
                Q(cattle__farm=request.user.farm) |
                Q(is_farm_wide=True, veterinarian__farm=request.user.farm)
            ).distinct()

        # Debug logging
        print(f"Treatments count: {treatments.count()}")
        print(f"Vaccinations count: {vaccinations.count()}")
        print(f"Periodic treatments count: {periodic_treatments.count()}")
        print(f"Periodic vaccinations count: {periodic_vaccinations.count()}")
        
        # Print the actual SQL queries
        print(f"Treatments query: {treatments.query}")
        print(f"Vaccinations query: {vaccinations.query}")

        data = {
            'treatments': TreatmentRecordSerializer(treatments, many=True).data,
            'vaccinations': VaccinationRecordSerializer(vaccinations, many=True).data,
            'periodic_treatments': PeriodicTreatmentRecordSerializer(periodic_treatments, many=True).data,
            'periodic_vaccinations': PeriodicVaccinationRecordSerializer(periodic_vaccinations, many=True).data,
        }
        return Response(data)
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error in get_cattle_health_records: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_gestation_check(request):
    """Create a new gestation check record"""
    try:
        # Validate cattle ownership
        try:
            cattle = Cattle.objects.get(
                pk=request.data.get('cattle'),
                farm=request.user.farm
            )
        except Cattle.DoesNotExist:
            return Response(
                {"error": "Cattle not found or access denied"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Ensure cattle is pregnant
        if cattle.gestation_status not in ['pregnant', 'calving']:
            return Response(
                {"error": "Can only create gestation checks for pregnant cattle"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the check record
        serializer = GestationCheckSerializer(data={
            **request.data,
            'veterinarian': request.user.id
        })
        if serializer.is_valid():
            check = serializer.save()
            
            # Create alert if health status needs attention
            if check.health_status in ['attention', 'critical']:
                Alert.objects.create(
                    cattle=cattle,
                    message=f"Health check on {check.check_date} requires attention: {check.notes}",
                    priority='high' if check.health_status == 'critical' else 'medium',
                    due_date=timezone.now().date() + timedelta(days=1)
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in create_gestation_check: {str(e)}")
        return Response(
            {"error": "Failed to create gestation check"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_milestone(request, milestone_id):
    """Update a gestation milestone"""
    try:
        milestone = get_object_or_404(
            GestationMilestone,
            id=milestone_id,
            cattle__farm=request.user.farm
        )
        
        serializer = GestationMilestoneSerializer(
            milestone,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            updated_milestone = serializer.save()
            
            # If marking as completed, set completed date
            if updated_milestone.is_completed and not updated_milestone.completed_date:
                updated_milestone.completed_date = timezone.now().date()
                updated_milestone.save()
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in update_milestone: {str(e)}")
        return Response(
            {"error": "Failed to update milestone"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cattle_gestation_timeline(request, cattle_id):
    """Get detailed gestation timeline for a specific cattle"""
    try:
        cattle = get_object_or_404(
            Cattle.objects.prefetch_related(
                'gestation_milestones',
                'gestation_checks',
                'treatment_records',
                'vaccination_records'
            ),
            id=cattle_id,
            farm=request.user.farm
        )

        if cattle.gestation_status not in ['pregnant', 'calving']:
            return Response(
                {"error": "Cattle is not pregnant"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Combine all events into a timeline
        timeline_events = []

        # Add milestones
        for milestone in cattle.gestation_milestones.all():
            timeline_events.append({
                'date': milestone.due_date.isoformat(),
                'type': 'milestone',
                'title': milestone.get_milestone_type_display(),
                'description': milestone.description,
                'status': 'completed' if milestone.is_completed else 'pending'
            })

        # Add health checks
        for check in cattle.gestation_checks.all():
            timeline_events.append({
                'date': check.check_date.isoformat(),
                'type': 'health_check',
                'title': f'Week {check.gestation_week} Health Check',
                'description': check.notes,
                'status': check.health_status
            })

        # Add treatments
        for treatment in cattle.treatment_records.all():
            timeline_events.append({
                'date': treatment.treatment_date.isoformat(),
                'type': 'treatment',
                'title': treatment.treatment_name,
                'description': treatment.treatment_description,
                'status': 'completed'
            })

        # Add vaccinations
        for vaccination in cattle.vaccination_records.all():
            timeline_events.append({
                'date': vaccination.vaccination_date.isoformat(),
                'type': 'vaccination',
                'title': vaccination.vaccination_name,
                'status': 'completed'
            })

        # Sort events by date
        timeline_events.sort(key=lambda x: x['date'])

        return Response({
            'cattle_id': cattle.id,
            'ear_tag_no': cattle.ear_tag_no,
            'gestation_progress': cattle.get_gestation_progress(),
            'trimester': cattle.get_trimester(),
            'days_until_calving': cattle.get_days_until_calving(),
            'timeline_events': timeline_events
        })
    except Exception as e:
        print(f"Error in get_cattle_gestation_timeline: {str(e)}")
        return Response(
            {"error": "Failed to fetch gestation timeline"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
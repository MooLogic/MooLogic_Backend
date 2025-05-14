from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import Cattle, Insemination, BirthRecord, Alert, Farm
from .serializers import CattleSerializer, InseminationSerializer, BirthRecordSerializer, AlertSerializer, FarmSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_cattle(request):
    cattle = Cattle.objects.all()
    serializer = CattleSerializer(cattle, many=True)
    return Response({"count": cattle.count(), "results": serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cattle_by_id(request, pk):
    try:
        cattle = Cattle.objects.get(pk=pk)
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = CattleSerializer(cattle)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_cattle(request):
    serializer = CattleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cattle(request, pk):
    try:
        cattle = Cattle.objects.get(pk=pk)
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = CattleSerializer(cattle, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def partial_update_cattle(request, pk):
    try:
        cattle = Cattle.objects.get(pk=pk)
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = CattleSerializer(cattle, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cattle(request, pk):
    try:
        cattle = Cattle.objects.get(pk=pk)
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    cattle.delete()
    return Response({'message': 'Cattle deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_cattle_alerts(request, pk):
    try:
        cattle = Cattle.objects.get(pk=pk)
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    alerts = cattle.generate_alerts()
    for alert in alerts:
        Alert.objects.create(
            cattle=cattle,
            message=alert['message'],
            due_date=timezone.now().date(),
            priority=alert['priority']
        )
        if alert['priority'] == 'Emergency':
            # Trigger SMS and phone call notification (placeholder)
            pass
    return Response({'alerts': alerts})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cattle_gestation_status(request, pk):
    try:
        cattle = Cattle.objects.get(pk=pk)
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found'}, status=status.HTTP_404_NOT_FOUND)
    cattle.update_gestation_status()
    return Response({'status': 'Gestation status updated successfully.'})


# Insemination Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_inseminations(request):
    inseminations = Insemination.objects.all()
    serializer = InseminationSerializer(inseminations, many=True)
    return Response({"count": inseminations.count(), "results": serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_insemination_by_id(request, pk):
    try:
        insemination = Insemination.objects.get(pk=pk)
    except Insemination.DoesNotExist:
        return Response({'error': 'Insemination not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = InseminationSerializer(insemination)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_insemination(request):
    data = {
        'cattle': request.data.get('cattle'),
        'insemination_date': request.data.get('insemination_date'),
        'bull_id': request.data.get('bull_id'),
        'insemination_type': request.data.get('insemination_type'),
        'insemination_method': request.data.get('insemination_method'),

        'notes': request.data.get('notes')
    }
    serializer = InseminationSerializer(data=data)
    print(data)
    cattle = Cattle.objects.get(pk=request.data['cattle'])
    print(cattle)
    if serializer.is_valid():
        # Save the insemination and update the Cattle model
        cattle = Cattle.objects.get(pk=request.data['cattle'])
        insemination = serializer.save()
        print("insemination" , insemination)
        cattle.last_insemination_date = insemination.insemination_date
        cattle.gestation_status = "pregnant"
        cattle.save()

        # Generate alerts for the insemination
        alerts = cattle.generate_alerts()
        for alert_message in alerts:
            Alert.objects.create(
                cattle=cattle,
                message=alert_message,
                due_date=timezone.now().date()
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print("data is not valid " , serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_insemination(request, two):
    try:
        insemination = Insemination.objects.get(pk=pk)
    except Insemination.DoesNotExist:
        return Response({'error': 'Insemination not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = InseminationSerializer(insemination, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def partial_update_insemination(request, pk):
    try:
        insemination = Insemination.objects.get(pk=pk)
    except Insemination.DoesNotExist:
        return Response({'error': 'Insemination not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = InseminationSerializer(insemination, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_insemination(request, pk):
    try:
        insemination = Insemination.objects.get(pk=pk)
    except Insemination.DoesNotExist:
        return Response({'error': 'Insemination not found'}, status=status.HTTP_404_NOT_FOUND)
    insemination.delete()
    return Response({'message': 'Insemination deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# BirthRecord Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_birth_records(request):
    birth_records = BirthRecord.objects.all()
    serializer = BirthRecordSerializer(birth_records, many=True)
    return Response({"count": birth_records.count(), "results": serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_birth_record_by_id(request, pk):
    try:
        birth_record = BirthRecord.objects.get(pk=pk)
    except BirthRecord.DoesNotExist:
        return Response({'error': 'Birth record not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = BirthRecordSerializer(birth_record)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_birth_record(request):
    serializer = BirthRecordSerializer(data=request.data)
    if serializer.is_valid():
        # Save the birth record and update the Cattle model
        birth_record = serializer.save()
        cattle = birth_record.cattle
        cattle.last_calving_date = birth_record.calving_date
        cattle.update_gestation_status()
        cattle.last_insemination_date = None
        cattle.expected_calving_date = None
        cattle.gestation_status = Cattle.GestationStatus.NOT_PREGNANT
        cattle.pregnancy_check_date = None
        cattle.estimate_expected_insemination_date()
        cattle.save()

        # Generate alerts for the birth record
        alerts = cattle.generate_alerts()
        for alert_message in alerts:
            Alert.objects.create(
                cattle=cattle,
                message=alert_message,
                due_date=timezone.now().date()
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_birth_record(request, pk):
    try:
        birth_record = BirthRecord.objects.get(pk=pk)
    except BirthRecord.DoesNotExist:
        return Response({'error': 'Birth record not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = BirthRecordSerializer(birth_record, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def partial_update_birth_record(request, pk):
    try:
        birth_record = BirthRecord.objects.get(pk=pk)
    except BirthRecord.DoesNotExist:
        return Response({'error': 'Birth record not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = BirthRecordSerializer(birth_record, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_birth_record(request, pk):
    try:
        birth_record = BirthRecord.objects.get(pk=pk)
    except BirthRecord.DoesNotExist:
        return Response({'error': 'Birth record not found'}, status=status.HTTP_404_NOT_FOUND)
    birth_record.delete()
    return Response({'message': 'Birth record deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# Alert Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_alerts(request):
    alerts = Alert.objects.all()
    serializer = AlertSerializer(alerts, many=True)
    return Response({"count": alerts.count(), "results": serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_alert_by_id(request, pk):
    try:
        alert = Alert.objects.get(pk=pk)
    except Alert.DoesNotExist:
        return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = AlertSerializer(alert)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_alert(request):
    serializer = AlertSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_alert(request, pk):
    try:
        alert = Alert.objects.get(pk=pk)
    except Alert.DoesNotExist:
        return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = AlertSerializer(alert, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def partial_update_alert(request, pk):
    try:
        alert = Alert.objects.get(pk=pk)
    except Alert.DoesNotExist:
        return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = AlertSerializer(alert, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_alert(request, pk):
    try:
        alert = Alert.objects.get(pk=pk)
    except Alert.DoesNotExist:
        return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
    alert.delete()
    return Response({'message': 'Alert deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
############################################################################################################################################################

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
        farm_code = "FARM" + str(Farm.objects.count() + 1)
        serializer.validated_data['farm_code'] = farm_code
        farm = serializer.save()
        request.user.farm = farm
        request.user.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_farm(request, pk):
    try:
        farm = Farm.objects.get(pk=pk)
    except Farm.DoesNotExist:
        return Response({'error': 'Farm not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = FarmSerializer(farm)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_farm(request, pk):
    try:
        farm = Farm.objects.get(pk=pk)
        if request.user.farm != farm:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    except Farm.DoesNotExist:
        return Response({'error': 'Farm not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = FarmSerializer(farm, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_farm(request, pk):
    try:
        farm = Farm.objects.get(pk=pk)
        if request.user.farm != farm:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    except Farm.DoesNotExist:
        return Response({'error': 'Farm not found'}, status=status.HTTP_404_NOT_FOUND)
    farm.delete()
    return Response({'message': 'Farm deleted successfully'}, status=status.HTTP_204_NO_CONTENT)



from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Cattle, Insemination, BirthRecord, Alert, Farm
from .serializers import CattleSerializer, InseminationSerializer, BirthRecordSerializer, AlertSerializer, FarmSerializer


class CattleViewSet(viewsets.ModelViewSet):
    queryset = Cattle.objects.all()
    serializer_class = CattleSerializer

    @action(detail=True, methods=['get'])
    def generate_alerts(self, request, pk=None):
        cattle = self.get_object()
        alerts = cattle.generate_alerts()
        for alert in alerts:
            Alert.objects.create(
                cattle=cattle,
                message=alert['message'],
                due_date=timezone.now().date(),
                priority=alert['priority']
            )
            if alert['priority'] == 'Emergency':
                # Trigger SMS and phone call notification
                pass
        return Response({'alerts': alerts})

    @action(detail=True, methods=['post'])
    def update_gestation_status(self, request, pk=None):
        cattle = self.get_object()
        cattle.update_gestation_status()
        return Response({'status': 'Gestation status updated successfully.'})

class InseminationViewSet(viewsets.ModelViewSet):
    queryset = Insemination.objects.all()
    serializer_class = InseminationSerializer

    def perform_create(self, serializer):
        # Save the insemination and update the Cattle model
        insemination = serializer.save()
        cattle = insemination.cattle
        cattle.last_insemination_date = insemination.insemination_date
        cattle.update_gestation_status()
        cattle.save()

        # Generate alerts for the insemination
        alerts = cattle.generate_alerts()
        for alert_message in alerts:
            Alert.objects.create(
                cattle=cattle,
                message=alert_message,
                due_date=timezone.now().date()
            )


class BirthRecordViewSet(viewsets.ModelViewSet):
    queryset = BirthRecord.objects.all()
    serializer_class = BirthRecordSerializer

    def perform_create(self, serializer):
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


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

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



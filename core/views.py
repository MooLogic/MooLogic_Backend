from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Cattle, Insemination, BirthRecord, Alert
from .serializers import CattleSerializer, InseminationSerializer, BirthRecordSerializer, AlertSerializer

class CattleViewSet(viewsets.ModelViewSet):
    queryset = Cattle.objects.all()
    serializer_class = CattleSerializer

    @action(detail=True, methods=['get'])
    def generate_alerts(self, request, pk=None):
        # Get the Cattle object by id
        cattle = self.get_object()
        alerts = cattle.generate_alerts()

        # Create Alert instances for each alert
        for alert_message in alerts:
            Alert.objects.create(
                cattle=cattle,
                message=alert_message,
                due_date=timezone.now().date()
            )

        # Return the alerts
        return Response({'alerts': alerts})

    @action(detail=True, methods=['post'])
    def update_gestation_status(self, request, pk=None):
        # Get the Cattle object by id
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
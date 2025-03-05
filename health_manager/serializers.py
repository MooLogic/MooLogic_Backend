from rest_framework import serializers
from .models import TreatmentRecord, VaccinationRecord, PeriodicVaccinationRecord

class TreatmentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentRecord
        fields = '__all__'

class VaccinationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationRecord
        fields = '__all__'

class PeriodicVaccinationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicVaccinationRecord
        fields = '__all__'

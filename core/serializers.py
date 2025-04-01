from rest_framework import serializers
from .models import Cattle, Insemination, BirthRecord, Alert, Farm

class CattleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cattle
        fields = '__all__'

class InseminationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insemination
        fields = '__all__'

class BirthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirthRecord
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'
        
class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = '__all__'
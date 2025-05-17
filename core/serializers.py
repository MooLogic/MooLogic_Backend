from rest_framework import serializers
from .models import Cattle, Insemination, BirthRecord, Alert, Farm

from rest_framework import serializers
from .models import Cattle

from rest_framework import serializers
from .models import Cattle

class CattleSerializer(serializers.ModelSerializer):
    last_insemination_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'],
        required=False,
        allow_null=True
    )
    last_calving_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'],
        required=False,
        allow_null=True
    )
    expected_calving_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'],
        required=False,
        allow_null=True
    )
    expected_insemination_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'],
        required=False,
        allow_null=True
    )

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
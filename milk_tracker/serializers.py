from rest_framework import serializers

from .models import Milk_record

class Milk_recordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milk_record
        fields = '__all__'
# serializers.py

from rest_framework import serializers
from .models import FinancialRecord, Farm, FinancialCategory, ProfitSnapshot

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = ['id', 'name']

class FinancialCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialCategory
        fields = ['id', 'name', 'is_income']

    def validate_name(self, value):
        
        #Check that the category name is unique.
        
        if FinancialCategory.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return value

class FinancialRecordSerializer(serializers.ModelSerializer):
    farm = FarmSerializer(read_only=True)
    category = FinancialCategorySerializer(read_only=True)
    farm_id = serializers.PrimaryKeyRelatedField(queryset=Farm.objects.all(), source='farm', write_only=True)
    category_name = serializers.CharField(write_only=True, max_length=50)  # New field

    recorded_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FinancialRecord
        fields = [
            'id', 'farm', 'farm_id', 'category', 'category_name', # Changed 'category_id' to 'category_name'
            'amount', 'description', 'date', 'recorded_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['date', 'recorded_by', 'created_at', 'updated_at', 'category'] #Added category to readonly field

    def create(self, validated_data):
        category_name = validated_data.pop('category_name')
        farm = validated_data.pop('farm') #Extract farm object to pass to the FinancialRecordSerializer
        try:
            category = FinancialCategory.objects.get(name__iexact=category_name)
        except FinancialCategory.DoesNotExist:
            category = FinancialCategory.objects.create(name=category_name, is_income=validated_data['category'].is_income) #This is very important, you need to pass the boolean if category doesnt exists.

        financial_record = FinancialRecord.objects.create(farm=farm, category=category, **validated_data)
        return financial_record



class ProfitSnapshotSerializer(serializers.ModelSerializer):
    farm = FarmSerializer(read_only=True)
    farm_id = serializers.PrimaryKeyRelatedField(queryset=Farm.objects.all(), source='farm', write_only=True)

    class Meta:
        model = ProfitSnapshot
        fields = ['id', 'farm', 'farm_id', 'total_income', 'total_expense', 'net_profit', 'date']
        read_only_fields = ['date']
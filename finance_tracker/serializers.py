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

class FinancialRecordSerializer(serializers.ModelSerializer):
    farm = FarmSerializer(read_only=True)
    category = FinancialCategorySerializer(read_only=True)
    farm_id = serializers.PrimaryKeyRelatedField(queryset=Farm.objects.all(), source='farm', write_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=FinancialCategory.objects.all(), source='category', write_only=True)
    recorded_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FinancialRecord
        fields = [
            'id', 'farm', 'farm_id', 'category', 'category_id',
            'amount', 'description', 'date', 'recorded_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['date', 'recorded_by', 'created_at', 'updated_at']

class ProfitSnapshotSerializer(serializers.ModelSerializer):
    farm = FarmSerializer(read_only=True)
    farm_id = serializers.PrimaryKeyRelatedField(queryset=Farm.objects.all(), source='farm', write_only=True)

    class Meta:
        model = ProfitSnapshot
        fields = ['id', 'farm', 'farm_id', 'total_income', 'total_expense', 'net_profit', 'date']
        read_only_fields = ['date']
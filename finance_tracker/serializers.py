from rest_framework import serializers
from .models import Farm, IncomeRecord, ExpenseRecord, ProfitSnapshot
from django.contrib.auth import get_user_model

User = get_user_model()

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = ['id', 'name', 'owner', 'created_at']

class IncomeRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeRecord
        fields = ['id', 'category_name', 'amount', 'description', 'date', 'recorded_by', 'created_at', 'updated_at']

class ExpenseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseRecord
        fields = ['id', 'category_name', 'amount', 'description', 'date', 'recorded_by', 'created_at', 'updated_at']

class ProfitSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfitSnapshot
        fields = ['id', 'total_income', 'total_expense', 'net_profit', 'date']

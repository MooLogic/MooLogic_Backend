from rest_framework import viewsets,permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import FinancialRecord, ProfitSnapshot, Farm, FinancialCategory
from .serializers import FinancialRecordSerializer, ProfitSnapshotSerializer
from datetime import date

class FinancialRecordViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialRecordSerializer
    permission_classes = [permissions.IsAuthenticated]  # Require authenticated users

    def get_queryset(self):
        return FinancialRecord.objects.all()

    def perform_create(self, serializer):
        farm_id = serializer.validated_data['farm'].id
        if not Farm.objects.filter(id=farm_id).exists():
            owner = self.request.user  # Use the authenticated user
            farm = Farm(id=farm_id, name=f"Test Farm {farm_id}", owner=owner)
            farm.save()

        category_id = serializer.validated_data['category'].id
        if not FinancialCategory.objects.filter(id=category_id).exists():
            category = FinancialCategory(id=category_id, name="Milk Sales", is_income=True)
            category.save()

        serializer.save(recorded_by=self.request.user)  # Set recorded_by to authenticated user

    @action(detail=False, methods=['get'])
    def summary(self, request):
        queryset = self.get_queryset()
        total_income = queryset.filter(category__is_income=True).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = queryset.filter(category__is_income=False).aggregate(Sum('amount'))['amount__sum'] or 0
        profitability = total_income - total_expense

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'profitability': profitability,
            'calculated_on': date.today()
        })

class ProfitSnapshotViewSet(viewsets.ModelViewSet):
    serializer_class = ProfitSnapshotSerializer
    permission_classes = []

    def get_queryset(self):
        return ProfitSnapshot.objects.all()

    @action(detail=False, methods=['post'])
    def generate_snapshot(self, request):
        farm_id = request.data.get('farm_id')
        today = date.today()

        try:
            farm = Farm.objects.get(id=farm_id)
            records = FinancialRecord.objects.filter(farm=farm, date__lte=today)
            total_income = records.filter(category__is_income=True).aggregate(Sum('amount'))['amount__sum'] or 0
            total_expense = records.filter(category__is_income=False).aggregate(Sum('amount'))['amount__sum'] or 0

            snapshot = ProfitSnapshot.objects.create(
                farm=farm,
                total_income=total_income,
                total_expense=total_expense,
                net_profit=total_income - total_expense,
            )
            serializer = ProfitSnapshotSerializer(snapshot)
            return Response(serializer.data, status=201)
        except Farm.DoesNotExist:
            return Response({"error": "Farm not found"}, status=404)
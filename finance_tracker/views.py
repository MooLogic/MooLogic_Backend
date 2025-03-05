from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import FinancialRecord, ProfitSnapshot, Farm, FinancialCategory
from .serializers import FinancialRecordSerializer, ProfitSnapshotSerializer
from datetime import date

class FinancialRecordViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter by farm and user
        farm_id = self.request.query_params.get('farm_id')
        queryset = FinancialRecord.objects.filter(recorded_by=self.request.user)  # Only records by this user

        if farm_id:
            queryset = queryset.filter(farm__id=farm_id)
        return queryset

    def perform_create(self, serializer):
        farm = serializer.validated_data['farm'] #Get farm from serializer
        #Ensure farm exists
        if not Farm.objects.filter(id=farm.id).exists():
            owner = self.request.user  # Use the authenticated user
            farm = Farm(id=farm.id, name=f"Test Farm {farm.id}", owner=owner)
            farm.save()

        serializer.save(recorded_by=self.request.user)

    @action(detail=False, methods=['post'])
    def income(self, request):
        serializer = FinancialRecordSerializer(data=request.data, context={'request': request}) #added context
        if serializer.is_valid():
            category_name = serializer.validated_data['category_name']
            try:
                category = FinancialCategory.objects.get(name__iexact=category_name)

                if not category.is_income:
                    return Response({"error": "Category must be an income category."}, status=status.HTTP_400_BAD_REQUEST)

            except FinancialCategory.DoesNotExist:
                #If category doesnt exist it means the value of is_income is not specified.
                return Response({"error": "Category Does Not Exist and no is_income value provided, please create category first"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(recorded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def expense(self, request):
        serializer = FinancialRecordSerializer(data=request.data, context={'request': request}) #added context
        if serializer.is_valid():
            category_name = serializer.validated_data['category_name']
            try:
                category = FinancialCategory.objects.get(name__iexact=category_name)
                if category.is_income:
                    return Response({"error": "Category must be an expense category."}, status=status.HTTP_400_BAD_REQUEST)
            except FinancialCategory.DoesNotExist:
                #If category doesnt exist it means the value of is_income is not specified.
                return Response({"error": "Category Does Not Exist and no is_income value provided, please create category first"}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(recorded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        farm_id = request.query_params.get('farm_id')
        if not farm_id:
            return Response({"error": "farm_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            farm = Farm.objects.get(id=farm_id)
        except Farm.DoesNotExist:
            return Response({"error": "Farm not found"}, status=status.HTTP_404_NOT_FOUND)

        queryset = FinancialRecord.objects.filter(farm=farm, recorded_by=self.request.user) # Records only for this user
        total_income = queryset.filter(category__is_income=True).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = queryset.filter(category__is_income=False).aggregate(Sum('amount'))['amount__sum'] or 0
        profitability = total_income - total_expense

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'profitability': profitability,
            'calculated_on': date.today()
        })

    # New endpoint for profit alert
    @action(detail=False, methods=['get'])
    def profit_alert(self, request):
        farm_id = request.query_params.get('farm_id')
        if not farm_id:
            return Response({"error": "farm_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            farm = Farm.objects.get(id=farm_id)
        except Farm.DoesNotExist:
            return Response({"error": "Farm not found"}, status=status.HTTP_404_NOT_FOUND)

        # Calculate profitability based on user's records
        queryset = FinancialRecord.objects.filter(farm=farm, recorded_by=self.request.user)
        total_income = queryset.filter(category__is_income=True).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = queryset.filter(category__is_income=False).aggregate(Sum('amount'))['amount__sum'] or 0
        profitability = total_income - total_expense

        # Check if profit is negative and return appropriate response
        if profitability < 0:
            return Response({
                "alert": "Warning: The farm is not in a profitable state.",
                "profitability": profitability,
                "checked_on": date.today()
            })
        else:
            return Response({
                "message": "The farm is in a profitable state.",
                "profitability": profitability,
                "checked_on": date.today()
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
            records = FinancialRecord.objects.filter(farm=farm)  # All records for the farm, by any user
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
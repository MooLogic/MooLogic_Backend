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
    
    @action(detail=False, methods=['post'])
    def income_summary(self, request):
        # Check both query params and request body for farm_id
        farm_id = request.query_params.get('farm_id') or request.data.get('farm_id')
        if not farm_id:
            return Response({"error": "farm_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            farm = Farm.objects.get(id=farm_id)
        except Farm.DoesNotExist:
            return Response({"error": "Farm not found"}, status=status.HTTP_404_NOT_FOUND)
        
        queryset = FinancialRecord.objects.filter(farm=farm, recorded_by=self.request.user)
        # Fix the aggregate syntax (it was using incorrect syntax)
        total_income = queryset.filter(category__is_income=True).aggregate(Sum('amount'))['amount__sum'] or 0
        
        return Response({
            'Total Income': total_income
        })
    @action(detail=False, methods=['post'])
    def income_breakdown(self, request):
        farm_id = request.query_params.get('farm_id')
        if not farm_id:
            return Response({"error": "farm_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            farm = Farm.objects.get(id=farm_id)
        except Farm.DoesNotExist:
            return Response({"error": "Farm not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get all income records for the farm by the authenticated user
        queryset = FinancialRecord.objects.filter(farm=farm, recorded_by=self.request.user, category__is_income=True)
        
        if not queryset.exists():
            return Response({"message": "No income records found for this farm"}, status=status.HTTP_200_OK)
        
        # Calculate total income
        total_income = queryset.aggregate(Sum('amount'))['amount__sum'] or 0
        if total_income == 0:
            return Response({"message": "Total income is zero, no breakdown available"}, status=status.HTTP_200_OK)
        
        # Group by category and calculate percentages
        income_Breakdown = {}
        for record in queryset:
            category_name = record.category.name
            amount = record.amount
            income_Breakdown[category_name] = income_Breakdown.get(category_name, 0) + amount
        
        # Calculate percentages
        breakdown = {
            category: round((amount / total_income) * 100, 2)
            for category, amount in income_Breakdown.items()
        }
        
        # Prepare response data
        response_data = {
            "title": "Income Sources",
            "subtitle": "Breakdown of income by source",
            "breakdown": breakdown,
            "total_income": total_income,
            "calculated_on": date.today()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def expense_breakdown(self, request):
        farm_id = request.query_params.get('farm_id')
        if not farm_id:
            return Response({"error": "farm_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            farm = Farm.objects.get(id=farm_id)
        except Farm.DoesNotExist:
            return Response({"error": "Farm not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get all income records for the farm by the authenticated user
        queryset = FinancialRecord.objects.filter(farm=farm, recorded_by=self.request.user, category__is_income=False)
        
        if not queryset.exists():
            return Response({"message": "No expense records found for this farm"}, status=status.HTTP_200_OK)
        
        # Calculate total income
        total_expense = queryset.aggregate(Sum('amount'))['amount__sum'] or 0
        if total_expense == 0:
            return Response({"message": "Total expense is zero, no breakdown available"}, status=status.HTTP_200_OK)
        
        # Group by category and calculate percentages
        expense_Breakdown = {}
        for record in queryset:
            category_name = record.category.name
            amount = record.amount
            expense_Breakdown[category_name] = expense_Breakdown.get(category_name, 0) + amount
        
        # Calculate percentages
        breakdown = {
            category: round((amount / total_expense) * 100, 2)
            for category, amount in expense_Breakdown.items()
        }
        
        # Prepare response data
        response_data = {
            "title": "Expense Sources",
            "subtitle": "Breakdown of expense by source",
            "breakdown": breakdown,
            "total_expense": total_expense,
            "calculated_on": date.today()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)



    
    @action(detail=False, methods=['post'])
    def expense_summary(self, request):
        farm_id =request.query_params.get('farm_id') or request.data.get('farm_id')
        if not farm_id:
            return Response({"error": "farm_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            farm=Farm.objects.get(id=farm_id)
        except Farm.DoesNotExist:
            return Response({"error": "Farm not found"}, status=status.HTTP_404_NOT_FOUND)
        queryset=FinancialRecord.objects.filter(farm=farm, recorded_by=self.request.user)
        total_expense=queryset.filter(category__is_income=False).aggregate(Sum('amount'))['amount__sum'] or 0
        return Response({
            'Total Expense': total_expense
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
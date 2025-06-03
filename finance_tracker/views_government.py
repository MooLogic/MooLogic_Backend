from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import IncomeRecord, ExpenseRecord, ProfitSnapshot
from core.models import Farm

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_national_finance_stats(request):
    """
    Get national-level financial statistics:
    - Total income and expenses
    - Regional financial performance
    - Profit trends
    """
    if request.user.role != 'government':
        return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

    # Get statistics for last 3 months
    three_months_ago = timezone.now() - timedelta(days=90)
    
    # Total income and expenses
    total_income = IncomeRecord.objects.filter(
        created_at__gte=three_months_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_expenses = ExpenseRecord.objects.filter(
        created_at__gte=three_months_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Regional financial performance
    regional_performance = Farm.objects.values('region').annotate(
        total_income=Sum('incomerecord__amount'),
        total_expenses=Sum('expenserecord__amount'),
        total_farms=Count('id'),
        avg_income_per_farm=Sum('incomerecord__amount') / Count('id'),
        avg_expenses_per_farm=Sum('expenserecord__amount') / Count('id')
    )
    
    # Profit trends (monthly)
    profit_trend = []
    current_date = timezone.now()
    for month in range(3):  # Last 3 months
        start_date = current_date - timedelta(days=30*(month+1))
        end_date = current_date - timedelta(days=30*month)
        
        monthly_income = IncomeRecord.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_expenses = ExpenseRecord.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        profit_trend.append({
            "month_start": start_date.strftime('%Y-%m'),
            "month_end": end_date.strftime('%Y-%m'),
            "income": monthly_income,
            "expenses": monthly_expenses,
            "profit": monthly_income - monthly_expenses
        })
    
    return Response({
        "financial_summary": {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_profit": total_income - total_expenses
        },
        "regional_performance": list(regional_performance),
        "profit_trend": profit_trend,
        "last_updated": timezone.now()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_national_expense_categories(request):
    """
    Get national-level expense category distribution:
    - Top expense categories
    - Regional expense patterns
    """
    if request.user.role != 'government':
        return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

    # Get top expense categories
    top_categories = ExpenseRecord.objects.values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:10]
    
    # Regional expense patterns
    regional_categories = ExpenseRecord.objects.values(
        'category', 'farm__region'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('farm__region', '-total')
    
    return Response({
        "top_expense_categories": list(top_categories),
        "regional_expense_patterns": list(regional_categories),
        "last_updated": timezone.now()
    })

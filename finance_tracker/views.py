from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import IncomeRecord, ExpenseRecord, ProfitSnapshot, Farm
from django.db.models import Sum
from .serializers import IncomeRecordSerializer, ExpenseRecordSerializer, ProfitSnapshotSerializer
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
from datetime import datetime
#crud for the income record 
#create income record
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def create_income(request):
    if request.method == 'POST':
        data = request.data.copy()
        farm_id = data.get('farm_id')
        
        # Validate farm_id presence and type
        if not farm_id:
            return Response({'error': 'farm_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            farm_id = int(farm_id)  # Ensure farm_id is an integer
            farm = Farm.objects.get(id=farm_id)
        except ValueError:
            return Response({'error': 'farm_id must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        except Farm.DoesNotExist:
            # Additional debugging info
            farm_exists = Farm.objects.filter(id=farm_id).exists()
            if not farm_exists:
                return Response({'error': 'Farm with this ID does not exist'}, 
                              status=status.HTTP_404_NOT_FOUND)
            return Response({'error': 'Farm exists but is not owned by you'}, 
                          status=status.HTTP_403_FORBIDDEN)
            
        # Prepare data for serializer
        data['recorded_by'] = request.user.id
        data['farm'] = farm.id
        
        serializer = IncomeRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#up
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_income(request, income_id):  # Changed parameter name for clarity
    # Get the income record, ensuring it exists
    record = get_object_or_404(IncomeRecord, id=income_id)
    
    # Verify the user owns the farm associated with this record
   #if record.farm.owner != request.user:
        #return Response(
           # {"error": "You do not have permission to update this record"},
           # status=status.HTTP_403_FORBIDDEN
        #)
    
    # Update the record with partial data
    serializer = IncomeRecordSerializer(record, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#delete income record 
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_income (request, income_id):
    record = get_object_or_404(IncomeRecord, id=income_id)
    record.delete()
    return Response({'message': 'Income record deleted successfully'},status=status.HTTP_204_NO_CONTENT)


# total income
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def total_income(request):
     total_income = IncomeRecord.objects.filter(recorded_by=request.user).aggregate(sum=Sum('amount'))
     return Response(total_income)


#income breakdown
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def income_breakdown(request, farm_id):
    # Filter records by farm and user
    records = IncomeRecord.objects.filter(recorded_by=request.user)
    if not records.exists():
        return Response({'message': 'No income records found for this farm'}, status=status.HTTP_200_OK)
    total_income = records.aggregate(Sum('amount'))['amount__sum'] or 0
    if total_income == 0:
        return Response({'message': 'Total income is zero'}, status=status.HTTP_200_OK)
    breakdown = {}
    for record in records:
        breakdown[record.category_name] = breakdown.get(record.category_name, 0) + float(record.amount)
    breakdown = {cat: round((amt / float(total_income)) * 100, 2) for cat, amt in breakdown.items()}
    return Response({
        'title': 'Income Breakdown',
        'breakdown': breakdown,
        'total_income': float(total_income),  # Convert Decimal to float for JSON
        'calculated_on': date.today()
    })




#list of all income 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_income(request):
    records = IncomeRecord.objects.filter(recorded_by=request.user)
    serializer = IncomeRecordSerializer(records, many=True)
    return Response(serializer.data)
       
   
#crud for the expense record
#create expense record
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_expense(request):
    if request.method == 'POST':
        data = request.data.copy()
        farm_id = data.get('farm_id')
        
        # Validate farm_id presence and type
        if not farm_id:
            return Response({'error': 'farm_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            farm_id = int(farm_id)  # Ensure farm_id is an integer
            farm = Farm.objects.get(id=farm_id)
        except ValueError:
            return Response({'error': 'farm_id must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        except Farm.DoesNotExist:
            # Additional debugging info
            farm_exists = Farm.objects.filter(id=farm_id).exists()
            if not farm_exists:
                return Response({'error': 'Farm with this ID does not exist'}, 
                              status=status.HTTP_404_NOT_FOUND)
            return Response({'error': 'Farm exists but is not owned by you'}, 
                          status=status.HTTP_403_FORBIDDEN)
            
        # Prepare data for serializer
        data['recorded_by'] = request.user.id
        data['farm'] = farm.id
        
        serializer = ExpenseRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#update expense record
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_expense(request, expense_id):
    record = get_object_or_404(ExpenseRecord, id=expense_id)
    
    # Verify the user owns the farm associated with this record
  #  if record.farm.owner != request.user:
        #return Response(
           # {"error": "You do not have permission to update this record"},
          #  status=status.HTTP_403_FORBIDDEN
       # )
    
    # Update the record with partial data
    serializer = ExpenseRecordSerializer(record, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#delete expense record
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_expense(request, expense_id):
    record=get_object_or_404(ExpenseRecord, id=expense_id)
    record.delete()
    return Response({'message': 'expense deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# total expense
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def total_expense(request):
    total_expense = ExpenseRecord.objects.filter(recorded_by=request.user).aggregate(sum=Sum('amount'))
    return Response(total_expense)

#expense breakdown
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_breakdown(request, farm_id):
    records = ExpenseRecord.objects.filter(recorded_by=request.user)
    if not records.exists():
        return Response({'message': 'No expense records found for this farm'}, status=status.HTTP_200_OK)
    total_expense = records.aggregate(Sum('amount'))['amount__sum'] or 0
    if total_expense == 0:
        return Response({'message': 'Total expense is zero'}, status=status.HTTP_200_OK)
    breakdown = {}
    for record in records:
        breakdown[record.category_name] = breakdown.get(record.category_name, 0) + float(record.amount)
    breakdown = {cat: round((amt / float(total_expense)) * 100, 2) for cat, amt in breakdown.items()}
    return Response({
        'title': 'Expense Breakdown',
        'breakdown': breakdown,
        'total_expense': float(total_expense),  # Convert Decimal to float for JSON
        'calculated_on': date.today()
    })
#list of all expense records
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_expense(request):
    records = ExpenseRecord.objects.filter(recorded_by=request.user)
    serializer = ExpenseRecordSerializer(records, many=True)
    return Response(serializer.data)

#generate_profit_snapshot
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_profit_snapshot(request):
    if request.method == 'POST':
        farm_id = request.GET.get('farm_id')
        if not farm_id:
            return Response({'error': 'farm_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            farm = Farm.objects.get(id=farm_id)
        except Farm.DoesNotExist:
            return Response({'error': 'Farm not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)
        
        # Filter by the user who recorded it and the farm_id from the serializer context
        total_income = IncomeRecord.objects.filter(
            recorded_by=request.user,  
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_expense = ExpenseRecord.objects.filter(
            recorded_by=request.user,
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        snapshot = ProfitSnapshot.objects.create(
            total_income=total_income,
            total_expense=total_expense,
            net_profit=total_income - total_expense
        )
        return Response(ProfitSnapshotSerializer(snapshot).data, status=status.HTTP_201_CREATED)
    
    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#generate_profit_snapshot_with_alerts
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_profit_snapshot_with_alerts(request):
    if request.method == 'POST':
        farm_id = request.GET.get('farm_id')
        if not farm_id:
            return Response({'error': 'farm_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            farm = Farm.objects.get(id=farm_id)
        except Farm.DoesNotExist:
            return Response({'error': 'Farm not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate totals using recorded_by (matches your working version)
        total_income = IncomeRecord.objects.filter(
            recorded_by=request.user
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_expense = ExpenseRecord.objects.filter(
            recorded_by=request.user
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        net_profit = total_income - total_expense
        
        # Create the snapshot
        snapshot = ProfitSnapshot.objects.create(
            total_income=total_income,
            total_expense=total_expense,
            net_profit=net_profit
        )
        
        # Serialize the snapshot
        response_data = ProfitSnapshotSerializer(snapshot).data
        alerts = []

        # Alert 1: Negative Profit
        if net_profit < 0:
            alerts.append("Alert: Profit is negative for this farm.")

        # Get the previous snapshot for comparison
        previous_snapshot = ProfitSnapshot.objects.exclude(
            id=snapshot.id
        ).order_by('-date').first()
        
        if previous_snapshot:
            previous_net_profit = previous_snapshot.net_profit
            
            # Alert 2: Profit Increase
            if net_profit > previous_net_profit:
                if previous_net_profit <= 0:
                    percent_increase = "N/A (previous profit was zero or negative)"
                else:
                    percent_increase = round(((net_profit - previous_net_profit) / abs(previous_net_profit)) * 100, 2)
                alerts.append(f"Alert: Profit increased by {percent_increase}% compared to previous snapshot.")
            
            # Alert 3: Profit Decrease (non-negative)
            elif net_profit < previous_net_profit and net_profit >= 0:
                percent_decrease = round(((previous_net_profit - net_profit) / previous_net_profit) * 100, 2)
                alerts.append(f"Alert: Profit decreased by {percent_decrease}% compared to previous snapshot.")

        # Add alerts to the response
        if alerts:
            response_data['alerts'] = alerts
        else:
            response_data['alerts'] = []  # Ensure alerts key is always present
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_finance_summary(request):
    """
    Get monthly finance summary for income and expenses
    """
    current_year = date.today().year
    
    # Initialize data structure for all months
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_data = {month: {'income': 0, 'expenses': 0} for month in months}
    
    # Get income records for current year
    income_records = IncomeRecord.objects.filter(
        recorded_by=request.user,
        date__year=current_year
    ).values('date', 'amount')
    
    # Get expense records for current year
    expense_records = ExpenseRecord.objects.filter(
        recorded_by=request.user,
        date__year=current_year
    ).values('date', 'amount')
    
    # Aggregate income by month
    for record in income_records:
        month = record['date'].strftime('%b')
        monthly_data[month]['income'] += float(record['amount'])
    
    # Aggregate expenses by month
    for record in expense_records:
        month = record['date'].strftime('%b')
        monthly_data[month]['expenses'] += float(record['amount'])
    
    # Format data for frontend
    formatted_data = [
        {
            'month': month,
            'income': monthly_data[month]['income'],
            'expenses': monthly_data[month]['expenses'],
            'cashFlow': monthly_data[month]['income'] - monthly_data[month]['expenses']
        }
        for month in months
    ]
    
    return Response(formatted_data)

    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_financial_records(request):
    """
    Export financial records in either PDF or Excel format
    """
    export_format = request.GET.get('format', 'pdf')
    
    # Get income and expense records
    income_records = IncomeRecord.objects.filter(recorded_by=request.user).values(
        'date', 'category_name', 'amount', 'description'
    ).order_by('date')
    
    expense_records = ExpenseRecord.objects.filter(recorded_by=request.user).values(
        'date', 'category_name', 'amount', 'description'
    ).order_by('date')

    if export_format.lower() == 'excel':
        # Create Excel workbook
        wb = Workbook()
        
        # Create Income sheet
        ws_income = wb.active
        ws_income.title = "Income Records"
        ws_income.append(['Date', 'Category', 'Amount (ETB)', 'Description'])
        
        for record in income_records:
            ws_income.append([
                record['date'].strftime('%Y-%m-%d'),
                record['category_name'],
                float(record['amount']),
                record['description']
            ])
        
        # Create Expense sheet
        ws_expense = wb.create_sheet("Expense Records")
        ws_expense.append(['Date', 'Category', 'Amount (ETB)', 'Description'])
        
        for record in expense_records:
            ws_expense.append([
                record['date'].strftime('%Y-%m-%d'),
                record['category_name'],
                float(record['amount']),
                record['description']
            ])
        
        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=financial_records.xlsx'
        wb.save(response)
        return response
    
    else:  # PDF format
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Add title
        current_date = datetime.now().strftime('%Y-%m-%d')
        title = f'Financial Records Report - {current_date}'
        elements.append(Table([[title]], style=[
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        # Income Records Table
        income_data = [['Date', 'Category', 'Amount (ETB)', 'Description']]
        for record in income_records:
            income_data.append([
                record['date'].strftime('%Y-%m-%d'),
                record['category_name'],
                f"{float(record['amount']):,.2f}",
                record['description']
            ])
        
        income_table = Table(income_data)
        income_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ]))
        
        elements.append(Table([['Income Records']], style=[
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(income_table)
        elements.append(Table([[' ']], style=[('BOTTOMPADDING', (0, 0), (-1, -1), 20)]))
        
        # Expense Records Table
        expense_data = [['Date', 'Category', 'Amount (ETB)', 'Description']]
        for record in expense_records:
            expense_data.append([
                record['date'].strftime('%Y-%m-%d'),
                record['category_name'],
                f"{float(record['amount']):,.2f}",
                record['description']
            ])
        
        expense_table = Table(expense_data)
        expense_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ]))
        
        elements.append(Table([['Expense Records']], style=[
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(expense_table)
        
        # Build PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=financial_records.pdf'
        response.write(pdf)
        return response 
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
create_income,update_income,delete_income,total_income,income_breakdown,list_income,
create_expense,update_expense,delete_expense,total_expense,expense_breakdown,list_expense,generate_profit_snapshot,generate_profit_snapshot_with_alerts

)

urlpatterns = [
    path('income/create/', create_income, name='create_income'),
    path('income/update/<int:income_id>/', update_income, name='update_income'),
    path('income/delete/<int:income_id>/', delete_income, name='delete_income'),
    path('income/total/', total_income, name='total_income'),
    path('income/breakdown/<int:farm_id>/', income_breakdown, name='income_breakdown'),
    path('income/list//', list_income, name='list_income'),

    path('expense/create/', create_expense, name='create_expense'),
    path('expense/update/<int:expense_id>/', update_expense, name='update_expense'),
    path('expense/delete/<int:expense_id>/', delete_expense, name='delete_expense'),
    path('expense/total/', total_expense, name='total_expense'),
    path('expense/breakdown/<int:farm_id>/', expense_breakdown, name='expense_breakdown'),
    path('expense/list//', list_expense, name='list_expense'),
    path('profit/snapshot/', generate_profit_snapshot, name='generate_profit_snapshot'),
    path('profit/snapshot/alerts/', generate_profit_snapshot_with_alerts, name='generate_profit_snapshot_with_alerts'),

]
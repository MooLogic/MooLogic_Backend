from django.urls import path
from . import views

urlpatterns = [
    path('milk-records/', views.milk_records, name='milk-records'),
    path('milk-production/<int:cattle_id>/', views.milk_production_by_cattle, name='milk-production-by-cattle'),
    path('milk-production/last-7-days/<int:cattle_id>/', views.milk_production_by_cattle_last_7_days, name='milk-production-last-7-days'),
    path('milk-production/last-30-days/<int:cattle_id>/', views.milk_production_by_cattle_last_30_days, name='milk-production-last-30-days'),
    path('milk-production/last-90-days/<int:cattle_id>/', views.milk_production_by_cattle_last_90_days, name='milk-production-last-90-days'),
    path('milk-production/last-300-days/<int:cattle_id>/', views.milk_production_by_cattle_last_300_days, name='milk-production-last-300-days'),
    # Overall farm production
    path('farm-production/last-7-days/', views.farm_production_last_7_days, name='farm-production-last-7-days'),
    path('farm-production/last-30-days/', views.farm_production_last_30_days, name='farm-production-last-30-days'),
    path('farm-production/last-90-days/', views.farm_production_last_90_days, name='farm-production-last-90-days'),

    # General milk records
    path('milk-records/', views.milk_records, name='milk-records'),
    path('add-milk-record/', views.add_milk_record, name='add-milk-record'),
]
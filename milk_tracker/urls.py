from django.urls import path
from . import views

urlpatterns = [
    # Basic milk record management
    path('milk-records/', views.milk_records, name='milk-records'),
    path('add-milk-record/', views.add_milk_record, name='add-milk-record'),
    path('update-milk-record/<int:record_id>/', views.update_milk_record, name='update-milk-record'),
    
    # Cattle-specific milk records
    path('milk-production/<int:cattle_id>/', views.milk_production_by_cattle, name='milk-production-by-cattle'),
    
    # Milking schedule management
    path('cattle/<int:cattle_id>/schedule/', views.get_cattle_milking_schedule, name='cattle-milking-schedule'),
    path('cattle/<int:cattle_id>/settings/', views.update_cattle_milking_settings, name='update-milking-settings'),
    
    # Monitoring and alerts
    path('check-missing-records/', views.check_missing_records, name='check-missing-records'),
    
    # Lactating cattle endpoint
    path('lactating-cattle/', views.get_lactating_cattle, name='lactating-cattle'),
    
    # Production analysis endpoints (moved to milk_yield app)
    path('milk-production/last-7-days/<int:cattle_id>/', views.milk_production_by_cattle_last_7_days, name='milk-production-last-7-days'),
    path('milk-production/last-30-days/<int:cattle_id>/', views.milk_production_by_cattle_last_30_days, name='milk-production-last-30-days'),
    path('milk-production/last-90-days/<int:cattle_id>/', views.milk_production_by_cattle_last_90_days, name='milk-production-last-90-days'),
    path('milk-production/last-300-days/<int:cattle_id>/', views.milk_production_by_cattle_last_300_days, name='milk-production-last-300-days'),
    
    # Farm-wide production analysis (moved to milk_yield app)
    path('farm-production/last-7-days/', views.farm_production_last_7_days, name='farm-production-last-7-days'),
    path('farm-production/last-30-days/', views.farm_production_last_30_days, name='farm-production-last-30-days'),
    path('farm-production/last-90-days/', views.farm_production_last_90_days, name='farm-production-last-90-days'),
    path('today-production-stats/', views.get_today_production_stats, name='get_today_production_stats'),
]
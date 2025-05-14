# yourapp/urls.py
from django.urls import path
from .views import (
   
    list_cattle,
    get_cattle_by_id,
    create_cattle,
    update_cattle,
    partial_update_cattle,
    delete_cattle,
    generate_cattle_alerts,
    update_cattle_gestation_status,
    
    list_inseminations,
    get_insemination_by_id,
    create_insemination,
    update_insemination,
    partial_update_insemination,
    delete_insemination,
    
    list_birth_records,
    get_birth_record_by_id,
    create_birth_record,
    update_birth_record,
    partial_update_birth_record,
    delete_birth_record,

    list_alerts,
    get_alert_by_id,
    create_alert,
    update_alert,
    partial_update_alert,
    delete_alert,

    get_farms,
    create_farm,
    get_farm,
    update_farm,
    delete_farm,
)

urlpatterns = [
    # Cattle endpoints
    path('cattle/', list_cattle, name='list_cattle'),
    path('cattle/<int:pk>/', get_cattle_by_id, name='get_cattle_by_id'),
    path('cattle/create/', create_cattle, name='create_cattle'),
    path('cattle/<int:pk>/update/', update_cattle, name='update_cattle'),
    path('cattle/<int:pk>/partial-update/', partial_update_cattle, name='partial_update_cattle'),
    path('cattle/<int:pk>/delete/', delete_cattle, name='delete_cattle'),
    path('cattle/<int:pk>/generate-alerts/', generate_cattle_alerts, name='generate_cattle_alerts'),
    path('cattle/<int:pk>/update-gestation-status/', update_cattle_gestation_status, name='update_cattle_gestation_status'),
    # Insemination endpoints
    path('inseminations/', list_inseminations, name='list_inseminations'),
    path('inseminations/<int:pk>/', get_insemination_by_id, name='get_insemination_by_id'),
    path('inseminations/create/', create_insemination, name='create_insemination'),
    path('inseminations/<int:pk>/update/', update_insemination, name='update_insemination'),
    path('inseminations/<int:pk>/partial-update/', partial_update_insemination, name='partial_update_insemination'),
    path('inseminations/<int:pk>/delete/', delete_insemination, name='delete_insemination'),
    # BirthRecord endpoints
    path('birth-records/', list_birth_records, name='list_birth_records'),
    path('birth-records/<int:pk>/', get_birth_record_by_id, name='get_birth_record_by_id'),
    path('birth-records/create/', create_birth_record, name='create_birth_record'),
    path('birth-records/<int:pk>/update/', update_birth_record, name='update_birth_record'),
    path('birth-records/<int:pk>/partial-update/', partial_update_birth_record, name='partial_update_birth_record'),
    path('birth-records/<int:pk>/delete/', delete_birth_record, name='delete_birth_record'),
    # Alert endpoints
    path('alerts/', list_alerts, name='list_alerts'),
    path('alerts/<int:pk>/', get_alert_by_id, name='get_alert_by_id'),
    path('alerts/create/', create_alert, name='create_alert'),
    path('alerts/<int:pk>/update/', update_alert, name='update_alert'),
    path('alerts/<int:pk>/partial-update/', partial_update_alert, name='partial_update_alert'),
    path('alerts/<int:pk>/delete/', delete_alert, name='delete_alert'),
    # Farm endpoints
    path('farms/', get_farms, name='get_farms'),
    path('farms/create/', create_farm, name='create_farm'),
    path('farms/<int:pk>/', get_farm, name='get_farm'),
    path('farms/<int:pk>/update/', update_farm, name='update_farm'),
    path('farms/<int:pk>/delete/', delete_farm, name='delete_farm'),
]
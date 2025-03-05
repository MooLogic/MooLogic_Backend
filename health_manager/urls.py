from django.urls import path
from .views import (
    create_treatment_record, get_all_treatment_records, get_treatment_record_by_id, update_treatment_record, delete_treatment_record,
    create_vaccination_record, get_all_vaccination_records, get_vaccination_record_by_id, update_vaccination_record, delete_vaccination_record,
    create_periodic_vaccination_record, get_all_periodic_vaccination_records, get_periodic_vaccination_record_by_id, update_periodic_vaccination_record, delete_periodic_vaccination_record
)

urlpatterns = [
    # TreatmentRecord URLs
    path('trecords/', get_all_treatment_records, name='get_all_treatment_records'),
    path('trecords/create/', create_treatment_record, name='create_treatment_record'),
    path('trecords/<int:record_id>/', get_treatment_record_by_id, name='get_treatment_record_by_id'),
    path('trecords/<int:record_id>/update/', update_treatment_record, name='update_treatment_record'),
    path('trecords/<int:record_id>/delete/', delete_treatment_record, name='delete_treatment_record'),

    # VaccinationRecord URLs
    path('vrecords/', get_all_vaccination_records, name='get_all_vaccination_records'),
    path('vrecords/create/', create_vaccination_record, name='create_vaccination_record'),
    path('vrecords/<int:record_id>/', get_vaccination_record_by_id, name='get_vaccination_record_by_id'),
    path('vrecords/<int:record_id>/update/', update_vaccination_record, name='update_vaccination_record'),
    path('vrecords/<int:record_id>/delete/', delete_vaccination_record, name='delete_vaccination_record'),

    # PeriodicVaccinationRecord URLs
    path('pvrecords/', get_all_periodic_vaccination_records, name='get_all_periodic_vaccination_records'),
    path('pvrecords/create/', create_periodic_vaccination_record, name='create_periodic_vaccination_record'),
    path('pvrecords/<int:record_id>/', get_periodic_vaccination_record_by_id, name='get_periodic_vaccination_record_by_id'),
    path('pvrecords/<int:record_id>/update/', update_periodic_vaccination_record, name='update_periodic_vaccination_record'),
    path('pvrecords/<int:record_id>/delete/', delete_periodic_vaccination_record, name='delete_periodic_vaccination_record'),
]

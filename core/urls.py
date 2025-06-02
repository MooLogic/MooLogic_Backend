from django.urls import path
from .views import (
    list_cattle, list_pregnant_cattle, list_gestation_data, get_cattle_by_id, create_cattle, update_cattle, delete_cattle,
    generate_cattle_alerts, list_inseminations, create_insemination, list_birth_records, create_birth_record,
    list_alerts, get_farms, create_farm,
    create_treatment_record, get_all_treatment_records, get_treatment_record_by_id, update_treatment_record, delete_treatment_record,
    create_vaccination_record, get_all_vaccination_records, get_vaccination_record_by_id, update_vaccination_record, delete_vaccination_record,
    create_periodic_vaccination_record, get_all_periodic_vaccination_records, get_periodic_vaccination_record_by_id,
    update_periodic_vaccination_record, delete_periodic_vaccination_record,
    create_periodic_treatment_record, get_all_periodic_treatment_records, get_periodic_treatment_record_by_id,
    update_periodic_treatment_record, delete_periodic_treatment_record,
    get_cattle_health_records, get_pending_pregnancy_checks, update_insemination, delete_insemination,
    get_birth_record, update_birth_record, delete_birth_record, get_cattle_birth_history,
    get_cattle_gestation_timeline, create_gestation_check, update_milestone,
    get_unread_alerts, mark_alert_as_read, mark_all_alerts_as_read, delete_alert,
)

urlpatterns = [
    # Cattle URLs
    path('cattle/', list_cattle, name='list_cattle'),
    path('cattle/pregnant/', list_pregnant_cattle, name='list_pregnant_cattle'),
    path('cattle/gestation-data/', list_gestation_data, name='list_gestation_data'),
    path('cattle/<int:pk>/', get_cattle_by_id, name='get_cattle_by_id'),
    path('cattle/create/', create_cattle, name='create_cattle'),
    path('cattle/<int:pk>/update/', update_cattle, name='update_cattle'),
    path('cattle/<int:pk>/delete/', delete_cattle, name='delete_cattle'),
    path('cattle/<int:cattle_id>/alerts/', generate_cattle_alerts, name='generate_cattle_alerts'),
    path('cattle/<int:cattle_id>/health-records/', get_cattle_health_records, name='get_cattle_health_records'),

    # Insemination URLs
    path('inseminations/', list_inseminations, name='list_inseminations'),
    path('inseminations/create/', create_insemination, name='create_insemination'),
    path('inseminations/pending-checks/', get_pending_pregnancy_checks, name='get_pending_pregnancy_checks'),
    path('inseminations/<int:pk>/', update_insemination, name='update_insemination'),
    path('inseminations/<int:pk>/delete/', delete_insemination, name='delete_insemination'),

    # BirthRecord URLs
    path('birth-records/', list_birth_records, name='list_birth_records'),
    path('birth-records/create/', create_birth_record, name='create_birth_record'),
    path('birth-records/<int:pk>/', get_birth_record, name='get_birth_record'),
    path('birth-records/<int:pk>/update/', update_birth_record, name='update_birth_record'),
    path('birth-records/<int:pk>/delete/', delete_birth_record, name='delete_birth_record'),
    path('cattle/<int:cattle_id>/birth-history/', get_cattle_birth_history, name='get_cattle_birth_history'),

    # TreatmentRecord URLs
    path('treatments/', get_all_treatment_records, name='get_all_treatment_records'),
    path('treatments/create/', create_treatment_record, name='create_treatment_record'),
    path('treatments/<int:pk>/', get_treatment_record_by_id, name='get_treatment_record_by_id'),
    path('treatments/<int:pk>/update/', update_treatment_record, name='update_treatment_record'),
    path('treatments/<int:pk>/delete/', delete_treatment_record, name='delete_treatment_record'),

    # VaccinationRecord URLs
    path('vaccinations/', get_all_vaccination_records, name='get_all_vaccination_records'),
    path('vaccinations/create/', create_vaccination_record, name='create_vaccination_record'),
    path('vaccinations/<int:pk>/', get_vaccination_record_by_id, name='get_vaccination_record_by_id'),
    path('vaccinations/<int:pk>/update/', update_vaccination_record, name='update_vaccination_record'),
    path('vaccinations/<int:pk>/delete/', delete_vaccination_record, name='delete_vaccination_record'),

    # PeriodicVaccinationRecord URLs
    path('periodic-vaccinations/', get_all_periodic_vaccination_records, name='get_all_periodic_vaccination_records'),
    path('periodic-vaccinations/create/', create_periodic_vaccination_record, name='create_periodic_vaccination_record'),
    path('periodic-vaccinations/<int:pk>/', get_periodic_vaccination_record_by_id, name='get_periodic_vaccination_record_by_id'),
    path('periodic-vaccinations/<int:pk>/update/', update_periodic_vaccination_record, name='update_periodic_vaccination_record'),
    path('periodic-vaccinations/<int:pk>/delete/', delete_periodic_vaccination_record, name='delete_periodic_vaccination_record'),

    # PeriodicTreatmentRecord URLs
    path('periodic-treatments/', get_all_periodic_treatment_records, name='get_all_periodic_treatment_records'),
    path('periodic-treatments/create/', create_periodic_treatment_record, name='create_periodic_treatment_record'),
    path('periodic-treatments/<int:pk>/', get_periodic_treatment_record_by_id, name='get_periodic_treatment_record_by_id'),
    path('periodic-treatments/<int:pk>/update/', update_periodic_treatment_record, name='update_periodic_treatment_record'),
    path('periodic-treatments/<int:pk>/delete/', delete_periodic_treatment_record, name='delete_periodic_treatment_record'),

    # Alert URLs
    path('alerts/', list_alerts, name='list_alerts'),
    path('alerts/unread/', get_unread_alerts, name='get_unread_alerts'),
    path('alerts/<int:alert_id>/mark-read/', mark_alert_as_read, name='mark_alert_as_read'),
    path('alerts/mark-all-read/', mark_all_alerts_as_read, name='mark_all_alerts_as_read'),
    path('alerts/<int:alert_id>/', delete_alert, name='delete_alert'),

    # Farm URLs
    path('farms/', get_farms, name='get_farms'),
    path('farms/create/', create_farm, name='create_farm'),

    # Gestation Management URLs
    path('cattle/<int:cattle_id>/gestation-timeline/', get_cattle_gestation_timeline, name='get_cattle_gestation_timeline'),
    path('gestation-checks/create/', create_gestation_check, name='create_gestation_check'),
    path('gestation-milestones/<int:milestone_id>/update/', update_milestone, name='update_milestone'),
]
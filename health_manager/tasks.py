from celery import shared_task
from django.utils import timezone
from .models import PeriodicVaccinationRecord
from .utils import send_notification  # Assume this function sends SMS/email notifications

@shared_task
def check_due_vaccinations():
    """
    Celery task to check for due vaccinations and send notifications.
    """
    due_records = PeriodicVaccinationRecord.objects.filter(next_vaccination_date__lte=timezone.now().date(), notification_sent=False)
    for record in due_records:
        # Send notification
        send_notification(
            message=f"Vaccination {record.vaccination_name} is due for {record.veterinarian.username} on {record.next_vaccination_date}."
        )
        # Mark notification as sent
        record.notification_sent = True
        record.save()
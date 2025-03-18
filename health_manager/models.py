from django.db import models
from django.utils import timezone
from userauth.models import User

# Model for adding treatment records
class TreatmentRecord(models.Model):
    veterinarian = models.ForeignKey(User, verbose_name="veternerian", on_delete=models.CASCADE)
    treatment_name = models.CharField(max_length=100)
    treatment_description = models.TextField()
    treatment_date = models.DateField()
    treatment_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.treatment_name} - ({self.treatment_date})"

# Model to track vaccinations
class VaccinationRecord(models.Model):
    veterinarian = models.ForeignKey(User, verbose_name="veternerian", on_delete=models.CASCADE)
    vaccination_name = models.CharField(max_length=100)
    vaccination_date = models.DateField()
    vaccination_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.vaccination_name} - ({self.vaccination_date})"

# Model to track periodic vaccinations

class PeriodicVaccinationRecord(models.Model):
    veterinarian = models.ForeignKey(User, verbose_name="veterinarian", on_delete=models.CASCADE)
    vaccination_name = models.CharField(max_length=100)
    last_vaccination_date = models.DateField()
    next_vaccination_date = models.DateField(blank=True, null=True)
    interval_days = models.PositiveIntegerField(help_text="Interval in days between vaccinations.")
    notification_sent = models.BooleanField(default=False, help_text="Whether a notification has been sent for the next vaccination.")

    def save(self, *args, **kwargs):
        # Automatically calculate the next vaccination date if not provided
        if not self.next_vaccination_date:
            self.next_vaccination_date = self.last_vaccination_date + timezone.timedelta(days=self.interval_days)
        super().save(*args, **kwargs)

    def is_due_for_vaccination(self):
        """Check if the vaccination is due based on the current date."""
        return timezone.now().date() >= self.next_vaccination_date

    def __str__(self):
        return f"{self.vaccination_name} - (Next: {self.next_vaccination_date})"
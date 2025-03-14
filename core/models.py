from django.db import models
from datetime import timedelta
from django.utils import timezone
from userauth.models import User



class Cattle(models.Model):
    breed = models.CharField(max_length=100, help_text="The breed of the cattle (e.g., Holstein, Jersey, Local).", blank=True, null=True)
    birth_date = models.DateField(help_text="The birth date of the cattle.", blank=True, null=True)
    ear_tag_no = models.CharField(max_length=100, help_text="The ear tag number of the cattle.")
    dam_id = models.CharField(max_length=100, help_text="The dam ID of the cattle.", blank=True, null=True)
    sire_id = models.CharField(max_length=100, help_text="The sire ID of the cattle.", blank=True, null=True)
    picture = models.ImageField(upload_to='cattle_pictures/', null=True, blank=True, help_text="An optional image of the cattle.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    HEALTH_STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('sick', 'Sick'),
        ('recovering', 'Recovering'),
        ('unknown', 'Unknown'),
    ]
    health_status = models.CharField(max_length=20, choices=HEALTH_STATUS_CHOICES, default='unknown', help_text="The current health status of the cattle.", blank=True, null=True)

   
    # Gestation cycle fields
    GESTATION_STATUS_CHOICES = [
        ('not_pregnant', 'Not Pregnant'),
        ('pregnant', 'Pregnant'),
        ('calving', 'Calving'),
        ('dry', 'Dry'),
    ]
    gestation_status = models.CharField(max_length=20, choices=GESTATION_STATUS_CHOICES, default='not_pregnant', help_text="The current gestation status of the cattle.")

    # Last insemination and calving dates (updated automatically)
    last_insemination_date = models.DateField(help_text="The date of the last insemination.", blank=True, null=True)
    last_calving_date = models.DateField(help_text="The date of the last calving.", blank=True, null=True)

    #pregnancy check date
    pregnancy_check_date = models.DateField(help_text="The date of the last pregnancy check.", blank=True, null=True)

    # Feeding and medication details
    special_feeding_start_date = models.DateField(help_text="The start date of special feeding before calving.", blank=True, null=True)
    special_feeding_end_date = models.DateField(help_text="The end date of special feeding after calving.", blank=True, null=True)
    medication_schedule = models.TextField(blank=True, null=True, help_text="Medication and treatment schedule during gestation.")
    
    #expected calving date
    expected_calving_date = models.DateField(help_text="The expected calving date of the cattle.", blank=True, null=True)
    expected_insemination_date = models.DateField(help_text="The expected inservation date of the cattle.", blank=True, null=True)

    

    class Meta:
        verbose_name = "Cattle"
        verbose_name_plural = "Cattle"

    def __str__(self):
        return f"Cattle {self.id} - {self.breed} ({self.gender}) Ear Tag No: {self.ear_tag_no}"

    # Methods to estimate significant dates and generate alerts
    def estimate_pregnancy_check_date(self):
        if self.last_insemination_date:
            pregnancy_check_date = self.last_insemination_date + timedelta(days=30)  # Pregnancy check 30 days after insemination
            self.pregnancy_check_date = pregnancy_check_date  # Pregnancy check 30 days after insemination
            self.save()
            return pregnancy_check_date  # Pregnancy check 30 days after insemination
        return None

    def estimate_expected_calving_date(self):
        if self.last_insemination_date :
            expected_calving_date = self.last_insemination_date + timedelta(days=280)
            self.expected_calving_date = expected_calving_date
            self.save()# Average gestation period is 280 days
            return expected_calving_date # Average gestation period is 280 days
        return None

    

    def estimate_expected_insemination_date(self):
        if self.last_calving_date:
            expected_insemination_date = self.last_calving_date + timedelta(days=60)
            self.expected_insemination_date = expected_insemination_date
            self.save()
            return expected_insemination_date
        return None

    def estimate_special_feeding_dates(self):
        if self.estimate_expected_calving_date():
            start = self.estimate_expected_calving_date() - timedelta(days=21)
            end = self.estimate_expected_calving_date() + timedelta(days=14)
            self.special_feeding_start_date = start
            self.special_feeding_end_date = end
            self.save()
            return {
                'start': start,  # 3 weeks before calving
                'end': end,  # 2 weeks after calving
            }
        return None

    def update_gestation_status(self):
        if self.last_insemination_date:
            expected_calving_date = self.estimate_expected_calving_date()
            if expected_calving_date:
                today = timezone.now().date()
                if today >= expected_calving_date - timedelta(days=14):  # 2 weeks before calving
                    self.gestation_status = 'calving'
                elif today >= self.last_insemination_date + timedelta(days=30):  # After pregnancy check
                    self.gestation_status = 'pregnant'
                else:
                    self.gestation_status = 'not_pregnant'
            else:
                self.gestation_status = 'not_pregnant'
        else:
            self.gestation_status = 'not_pregnant'
        self.save()

    def generate_alerts(self):
        alerts = []
        today = timezone.now().date()

        # Pregnancy check alert
        pregnancy_check_date = self.estimate_pregnancy_check_date()
        if pregnancy_check_date:
            if today >= pregnancy_check_date - timedelta(days=7):  # Alert 7 days before
                alerts.append(f"Pregnancy check due on {pregnancy_check_date}.")

        # Expected calving alert
        expected_calving_date = self.estimate_expected_calving_date()
        if expected_calving_date:
            if today >= expected_calving_date - timedelta(days=14):  # Alert 2 weeks before
                alerts.append(f"Expected calving date is {expected_calving_date}.")

        # Special feeding alert
        feeding_dates = self.estimate_special_feeding_dates()
        if feeding_dates:
            if today >= feeding_dates['start'] - timedelta(days=7):  # Alert 1 week before special feeding starts
                alerts.append(f"Special feeding required from {feeding_dates['start']} to {feeding_dates['end']}.")

        # Next insemination alert
        
        if self.expected_insemination_date:
            if today >= self.expected_insemination_date - timedelta(days=14):  # Alert 2 weeks before
                alerts.append(f"Next insemination recommended around {self.expected_insemination_date}.")

        return alerts



class Insemination(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='inseminations', help_text="The cattle associated with this insemination.")
    insemination_date = models.DateField(help_text="The date of insemination.")
    insemination_type = models.CharField(max_length=50, choices=[('natural', 'Natural'), ('artificial', 'Artificial')], help_text="The type of insemination (natural or artificial).")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the insemination.")

    class Meta:
        verbose_name = "Insemination"
        verbose_name_plural = "Inseminations"

    def __str__(self):
        return f"Insemination for {self.cattle.ear_tag_no} on {self.insemination_date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the Cattle model with the latest insemination date
        self.cattle.last_insemination_date = self.insemination_date
        self.cattle.update_gestation_status()
        self.cattle.estimate_pregnancy_check_date()
        self.cattle.estimate_expected_calving_date()
        self.cattle.estimate_special_feeding_dates()
        self.cattle.generate_alerts()
        self.cattle.save()


class BirthRecord(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='birth_records', help_text="The cattle associated with this birth record.")
    calving_date = models.DateField(help_text="The date of calving.")
    calving_outcome = models.CharField(max_length=50, choices=[('successful', 'Successful'), ('complications', 'Complications')], help_text="The outcome of the calving.")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the calving.")

    class Meta:
        verbose_name = "Birth Record"
        verbose_name_plural = "Birth Records"

    def __str__(self):
        return f"Birth Record for {self.cattle.ear_tag_no} on {self.calving_date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the Cattle model with the latest calving date
        self.cattle.last_calving_date = self.calving_date
        self.cattle.update_gestation_status()
        self.cattle.save()


class Alert(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='alerts', help_text="The cattle associated with this alert.")
    message = models.TextField(help_text="The alert message.")
    due_date = models.DateField(help_text="The date when the alert is due.")
    is_read = models.BooleanField(default=False, help_text="Whether the alert has been read.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"

    def __str__(self):
        return f"Alert for {self.cattle.ear_tag_no} - {self.message}"


class Farm(models.Model):
    name = models.CharField(max_length=100, help_text="The name of the farm.")
    location = models.CharField(max_length=100, help_text="The location of the farm.")
    contact = models.CharField(max_length=100, help_text="The contact number of the farm.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Farm"
        verbose_name_plural = "Farms"

    def __str__(self):
        return f"{self.name} ({self.location})"
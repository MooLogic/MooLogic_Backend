from django.db import models
from datetime import timedelta
from django.utils import timezone



class Cattle(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
       
    ]

    LIFE_STAGE_CHOICES = [
        ('calf', 'Calf'),
        ('heifer', 'Heifer'),
        ('cow', 'Cow'),
        ('bull', 'Bull'),
    ]


    GESTATION_STATUS_CHOICES = [

        ('not_pregnant', 'Not Pregnant'),
        ('pregnant', 'Pregnant'),
        ('calving', 'Calving'),
    ]

    breed = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unknown')
    life_stage = models.CharField(max_length=10, choices=LIFE_STAGE_CHOICES, default='calf')
    ear_tag_no = models.CharField(max_length=100, unique=True)
    dam_id = models.CharField(max_length=100, blank=True, null=True)
    sire_id = models.CharField(max_length=100, blank=True, null=True)
    is_purchased = models.BooleanField(default=False)
    purchase_date = models.DateField(blank=True, null=True)
    purchase_source = models.CharField(max_length=255, blank=True, null=True)
    last_insemination_date = models.DateField(blank=True, null=True)
    last_calving_date = models.DateField(blank=True, null=True)
    expected_calving_date = models.DateField(blank=True, null=True)
    expected_insemination_date = models.DateField(blank=True, null=True)
    gestation_status = models.CharField(max_length=20, choices=GESTATION_STATUS_CHOICES, default='not_pregnant')
    health_status = models.CharField(max_length=20, choices=[('healthy', 'Healthy'), ('sick', 'Sick')], default='healthy')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_life_stage(self):
        if not self.birth_date:
            return
        age_in_months = (timezone.now().date() - self.birth_date).days // 30
        if self.gender == 'female':
            if age_in_months < 12:
                self.life_stage = 'calf'
            elif 12 <= age_in_months < 24:
                self.life_stage = 'heifer'
            elif age_in_months >= 24 and self.last_calving_date:
                self.life_stage = 'cow'
        elif self.gender == 'male':
            if age_in_months < 12:
                self.life_stage = 'calf'
            else:
                self.life_stage = 'bull'
        self.save()

    def update_gestation_status(self):
        if self.last_insemination_date:
            gestation_period = (timezone.now().date() - self.last_insemination_date).days
            if gestation_period < 280:
                self.gestation_status = 'pregnant'
            elif gestation_period >= 280:
                self.gestation_status = 'calving'
        else:
            self.gestation_status = 'not_pregnant'
        self.save()

    def estimate_expected_calving_date(self):
        if self.last_insemination_date:
            self.expected_calving_date = self.last_insemination_date + timedelta(days=280)
            self.save()
        return self.expected_calving_date

    def estimate_expected_insemination_date(self):
        if self.last_calving_date:
            self.expected_insemination_date = self.last_calving_date + timedelta(days=60)
            self.save()
        return self.expected_insemination_date

    def generate_alerts(self):
        alerts = []
        today = timezone.now().date()

        # Heifer first breeding alert
        if self.life_stage == 'heifer':
            age_in_months = (today - self.birth_date).days // 30
            if 15 <= age_in_months <= 18:
                alerts.append({'message': f"Heifer {self.ear_tag_no} is ready for first breeding.", 'priority': 'Medium'})

        # Pregnancy check alert
        if self.last_insemination_date:
            check_date = self.last_insemination_date + timedelta(days=30)
            if today >= check_date - timedelta(days=7):
                alerts.append({'message': f"Pregnancy check due for {self.ear_tag_no} on {check_date}.", 'priority': 'High'})

        # Expected calving alert
        if self.expected_calving_date:
            if today >= self.expected_calving_date - timedelta(days=14):
                alerts.append({'message': f"Cattle {self.ear_tag_no} is expected to calve on {self.expected_calving_date}.", 'priority': 'Emergency'})

        # Next insemination alert
        if self.expected_insemination_date:
            if today >= self.expected_insemination_date - timedelta(days=14):
                alerts.append({'message': f"Next insemination recommended around {self.expected_insemination_date} for {self.ear_tag_no}.", 'priority': 'Medium'})

        return alerts

    def save(self, *args, **kwargs):
        self.calculate_life_stage()
        self.update_gestation_status()
        self.estimate_expected_calving_date()
        self.estimate_expected_insemination_date()
        super().save(*args, **kwargs)


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
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Emergency', 'Emergency'),
    ]

    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='alerts')
    message = models.TextField()
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Low')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert for {self.cattle.ear_tag_no} - {self.message}"

    def send_notification(self):
        if self.priority == 'Emergency':
            # Implement SMS and phone call notification logic here
            pass
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
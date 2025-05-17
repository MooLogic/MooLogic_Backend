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
    ]

    GESTATION_STATUS_CHOICES = [
        ('not_pregnant', 'Not Pregnant'),
        ('pregnant', 'Pregnant'),
        
    ]

    breed = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='female')  # Default set to avoid 'unknown'
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

    def calculate_life_stage_value(self):
        if not self.birth_date:
            return self.life_stage
        age_in_months = (timezone.now().date() - self.birth_date).days // 30
        if self.gender == 'female':
            if age_in_months < 12:
                return 'calf'
            elif 12 <= age_in_months < 24:
                return 'heifer'
            elif age_in_months >= 24 and self.last_calving_date:
                return 'cow'
        elif self.gender == 'male':
            if age_in_months < 12:
                return 'calf'
            else:
                return 'bull'  # Consider adding 'bull' to choices
        return self.life_stage

    def calculate_gestation_status_value(self):
        if self.last_insemination_date:
            days = (timezone.now().date() - self.last_insemination_date).days
            if days < 280:
                return 'pregnant'
            else:
                return 'calving'
        return 'not_pregnant'

    def calculate_expected_calving_date(self):
        if self.last_insemination_date:
            return self.last_insemination_date + timedelta(days=280)
        return None

    def calculate_expected_insemination_date(self):
        if self.last_calving_date:
            return self.last_calving_date + timedelta(days=60)
        return None

    def generate_alerts(self):
        alerts = []
        today = timezone.now().date()

        if self.birth_date:
            age_in_months = (today - self.birth_date).days // 30

            if self.life_stage == 'heifer' and 15 <= age_in_months <= 18:
                alerts.append({'message': f"Heifer {self.ear_tag_no} is ready for first breeding.", 'priority': 'Medium'})

        if self.last_insemination_date:
            check_date = self.last_insemination_date + timedelta(days=30)
            if today >= check_date - timedelta(days=7):
                alerts.append({'message': f"Pregnancy check due for {self.ear_tag_no} on {check_date}.", 'priority': 'High'})

        if self.expected_calving_date and today >= self.expected_calving_date - timedelta(days=14):
            alerts.append({'message': f"Cattle {self.ear_tag_no} is expected to calve on {self.expected_calving_date}.", 'priority': 'Emergency'})

        if self.expected_insemination_date and today >= self.expected_insemination_date - timedelta(days=14):
            alerts.append({'message': f"Next insemination recommended around {self.expected_insemination_date} for {self.ear_tag_no}.", 'priority': 'Medium'})

        return alerts

    def save(self, *args, **kwargs):
        self.life_stage = self.calculate_life_stage_value()
        self.gestation_status = self.calculate_gestation_status_value()
        self.expected_calving_date = self.calculate_expected_calving_date()
        self.expected_insemination_date = self.calculate_expected_insemination_date()
        super().save(*args, **kwargs)


class Insemination(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='inseminations', null=True, blank=True)
    bull_id = models.CharField(max_length=100, blank=True, null=True)

    
    INSEMINATION_METHOD_CHOICES = [
        ('natural', 'Natural'),
        ('artificial', 'Artificial'),
    ]
    INSEMINATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ]
    insemination_method = models.CharField(max_length=50, choices=INSEMINATION_METHOD_CHOICES, default='natural', null=True, blank=True)
    insemination_status = models.CharField(max_length=50, choices=INSEMINATION_STATUS_CHOICES, default='pending', null=True, blank=True)
    insemination_date = models.DateField(auto_now_add=True)
    
    insemination_type = models.CharField(max_length=50, choices=[('natural', 'Natural'), ('artificial', 'Artificial')], null=True, blank=True)  
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Insemination for {self.cattle.ear_tag_no} on {self.insemination_date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cattle.last_insemination_date = self.insemination_date
        self.cattle.save()


class BirthRecord(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='birth_records')
    calving_date = models.DateField()
    calving_outcome = models.CharField(max_length=50, choices=[('successful', 'Successful'), ('complications', 'Complications')])
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Birth Record for {self.cattle.ear_tag_no} on {self.calving_date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cattle.last_calving_date = self.calving_date
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


class Farm(models.Model):
    name = models.CharField(max_length=100, unique=True)
    farm_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    location = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.location})"

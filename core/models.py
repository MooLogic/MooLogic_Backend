from django.db import models
from django.utils import timezone
from datetime import timedelta

class Farm(models.Model):
    name = models.CharField(max_length=100, unique=True)
    farm_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    location = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.location})"

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
        ('in_oestrus', 'In Oestrus'),
        ('missed_oestrus', 'Missed Oestrus'),
        ('pregnant', 'Pregnant'),
        ('dry_off', 'Dry Off'),
        ('calving', 'Calving'),
    ]
    GESTATION_STAGE_CHOICES = [
        ('not_pregnant', 'Not Pregnant'),
        ('first_trimester', 'First Trimester'),
        ('second_trimester', 'Second Trimester'),
        ('third_trimester', 'Third Trimester'),
        ('calving', 'Calving'),
    ]
    HEALTH_STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('sick', 'Sick'),
    ]
    MILKING_FREQUENCY_CHOICES = [
        ('once', 'Once a day'),
        ('twice', 'Twice a day'),
        ('thrice', 'Three times a day')
    ]

    farm = models.ForeignKey('Farm', on_delete=models.CASCADE)
    ear_tag_no = models.CharField(max_length=50, unique=True)
    breed = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    life_stage = models.CharField(max_length=10, choices=LIFE_STAGE_CHOICES)
    dam_id = models.CharField(max_length=50, blank=True)
    sire_id = models.CharField(max_length=50, blank=True)
    is_purchased = models.BooleanField(default=False)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_source = models.CharField(max_length=200, blank=True)
    last_insemination_date = models.DateField(null=True, blank=True)
    last_calving_date = models.DateField(null=True, blank=True)
    expected_calving_date = models.DateField(null=True, blank=True)
    expected_insemination_date = models.DateField(null=True, blank=True)
    gestation_status = models.CharField(
        max_length=20,
        choices=GESTATION_STATUS_CHOICES,
        default='not_pregnant'
    )
    gestation_stage = models.CharField(
        max_length=20,
        choices=GESTATION_STAGE_CHOICES,
        default='not_pregnant'
    )
    health_status = models.CharField(
        max_length=10,
        choices=HEALTH_STATUS_CHOICES,
        default='healthy'
    )
    photo = models.ImageField(upload_to='cattle_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    calving_count = models.IntegerField(default=0, help_text="Number of times this animal has given birth")
    current_lactation = models.IntegerField(default=0, help_text="Current lactation number")
    first_calving_date = models.DateField(null=True, blank=True, help_text="Date of first calving")
    average_calving_interval = models.FloatField(null=True, blank=True, help_text="Average interval between calvings in days")
    milking_frequency = models.CharField(
        max_length=10,
        choices=MILKING_FREQUENCY_CHOICES,
        default='twice'
    )
    custom_milking_times = models.JSONField(
        null=True, 
        blank=True,
        help_text='Custom milking times in 24-hour format. e.g. ["06:00", "14:00", "22:00"]'
    )
    avg_daily_milk = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text='Average daily milk production in liters'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ear_tag_no} - {self.breed}"

    def update_calving_stats(self):
        """Update calving statistics when a new birth record is added"""
        birth_records = self.birthrecord_set.all().order_by('calving_date')
        
        # Update calving count
        self.calving_count = birth_records.count()
        
        # Update current lactation
        self.current_lactation = self.calving_count
        
        # Update first calving date
        if birth_records.exists():
            self.first_calving_date = birth_records.first().calving_date
        
        # Calculate average calving interval
        if self.calving_count > 1:
            intervals = []
            previous_date = None
            for record in birth_records:
                if previous_date:
                    interval = (record.calving_date - previous_date).days
                    intervals.append(interval)
                previous_date = record.calving_date
            self.average_calving_interval = sum(intervals) / len(intervals)
        
        self.save()

    def get_lactation_status(self):
        """Get detailed lactation status including days in milk"""
        if not self.last_calving_date:
            return {
                'lactation_number': 0,
                'days_in_milk': 0,
                'status': 'not_lactating'
            }

        days_in_milk = (timezone.now().date() - self.last_calving_date).days
        
        if days_in_milk <= 3:
            status = 'colostrum'
        elif self.gestation_status == 'dry_off':
            status = 'dry'
        else:
            status = 'lactating'

        return {
            'lactation_number': self.current_lactation,
            'days_in_milk': days_in_milk,
            'status': status
        }

    def get_calving_history(self):
        """Get comprehensive calving history"""
        return {
            'total_calvings': self.calving_count,
            'first_calving_date': self.first_calving_date,
            'average_interval': self.average_calving_interval,
            'current_lactation': self.current_lactation,
            'records': [
                {
                    'calving_date': record.calving_date,
                    'calf_count': record.calf_count,
                    'outcome': record.calving_outcome,
                    'calf_details': {
                        'gender': record.calf_gender,
                        'weight': record.calf_weight,
                        'ear_tag': record.calf_ear_tag
                    }
                }
                for record in self.birthrecord_set.all().order_by('calving_date')
            ]
        }

    def get_reproductive_efficiency(self):
        """Calculate reproductive efficiency metrics"""
        if self.calving_count < 2:
            return None

        return {
            'average_calving_interval': self.average_calving_interval,
            'calving_rate': self.calving_count / ((timezone.now().date().year - self.birth_date.year) - 1) if self.birth_date else None,
            'first_calving_age': (self.first_calving_date - self.birth_date).days / 365 if self.first_calving_date and self.birth_date else None
        }

    def calculate_life_stage_value(self):
        if not self.birth_date:
            return self.life_stage
        age_in_months = (timezone.now().date() - self.birth_date).days // 30
        if self.gender == 'female':
            if age_in_months < 12:
                return 'calf'
            elif 12 <= age_in_months < 24:
                return 'heifer'
            elif age_in_months >= 24:
                return 'cow'
        elif self.gender == 'male':
            if age_in_months < 12:
                return 'calf'
            else:
                return 'bull'
        return self.life_stage

    def calculate_gestation_status_value(self):
        if self.last_insemination_date:
            days = (timezone.now().date() - self.last_insemination_date).days
            if days >= 270:
                return 'calving'
            elif days >= 0:
                return 'pregnant'
        return 'not_pregnant'

    def calculate_gestation_stage_value(self):
        if self.last_insemination_date:
            days = (timezone.now().date() - self.last_insemination_date).days
            if days >= 270:
                return 'calving'
            elif days >= 180:
                return 'third_trimester'
            elif days >= 90:
                return 'second_trimester'
            elif days >= 0:
                return 'first_trimester'
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
                alerts.append({
                    'message': f"Heifer {self.ear_tag_no} is ready for first breeding.",
                    'priority': 'Medium',
                    'due_date': today,
                })

        if self.last_insemination_date:
            check_date = self.last_insemination_date + timedelta(days=30)
            if today >= check_date - timedelta(days=7):
                alerts.append({
                    'message': f"Pregnancy check due for {self.ear_tag_no} on {check_date}.",
                    'priority': 'High',
                    'due_date': check_date,
                })

        if self.expected_calving_date and today >= self.expected_calving_date - timedelta(days=14):
            alerts.append({
                'message': f"Cattle {self.ear_tag_no} is expected to calve on {self.expected_calving_date}.",
                'priority': 'Emergency',
                'due_date': self.expected_calving_date,
            })

        if self.expected_insemination_date and today >= self.expected_insemination_date - timedelta(days=14):
            alerts.append({
                'message': f"Next insemination recommended around {self.expected_insemination_date} for {self.ear_tag_no}.",
                'priority': 'Medium',
                'due_date': self.expected_insemination_date,
            })

        # Periodic Vaccination Alerts
        for pv_record in self.periodic_vaccination_records.all():
            if pv_record.is_due_for_vaccination() and not pv_record.notification_sent:
                alerts.append({
                    'message': f"Periodic vaccination '{pv_record.vaccination_name}' due for {self.ear_tag_no} on {pv_record.next_vaccination_date}.",
                    'priority': 'High',
                    'due_date': pv_record.next_vaccination_date,
                })

        # Periodic Treatment Alerts
        for pt_record in self.periodic_treatment_records.all():
            if pt_record.is_due_for_treatment() and not pt_record.notification_sent:
                alerts.append({
                    'message': f"Periodic treatment '{pt_record.treatment_name}' due for {self.ear_tag_no} on {pt_record.next_treatment_date}.",
                    'priority': 'High',
                    'due_date': pt_record.next_treatment_date,
                })

        return alerts

    def save(self, *args, **kwargs):
        self.life_stage = self.calculate_life_stage_value()
        self.gestation_status = self.calculate_gestation_status_value()
        self.gestation_stage = self.calculate_gestation_stage_value()
        self.expected_calving_date = self.calculate_expected_calving_date()
        self.expected_insemination_date = self.calculate_expected_insemination_date()
        super().save(*args, **kwargs)

    def get_gestation_progress(self):
        """Calculate gestation progress as a percentage"""
        if not self.last_insemination_date or self.gestation_status == 'not_pregnant':
            return 0
        
        days_pregnant = (timezone.now().date() - self.last_insemination_date).days
        return min(round((days_pregnant / 280) * 100, 1), 100)

    def get_trimester(self):
        """Get current trimester number (1, 2, 3) or None if not pregnant"""
        if not self.last_insemination_date or self.gestation_status == 'not_pregnant':
            return None
        
        days_pregnant = (timezone.now().date() - self.last_insemination_date).days
        if days_pregnant <= 95:
            return 1
        elif days_pregnant <= 190:
            return 2
        else:
            return 3

    def get_days_until_calving(self):
        """Get number of days until expected calving"""
        if not self.expected_calving_date:
            return None
        return (self.expected_calving_date - timezone.now().date()).days

    def generate_gestation_milestones(self):
        """Generate or update gestation milestones based on insemination date"""
        if not self.last_insemination_date or self.gestation_status == 'not_pregnant':
            return

        # Clear existing incomplete milestones
        self.gestation_milestones.filter(is_completed=False).delete()

        # Define milestones
        milestones = [
            {
                'type': 'health_check',
                'days': 30,
                'description': 'First trimester health check'
            },
            {
                'type': 'vaccination',
                'days': 60,
                'description': 'First trimester vaccinations'
            },
            {
                'type': 'trimester_start',
                'days': 95,
                'description': 'Second trimester begins'
            },
            {
                'type': 'health_check',
                'days': 120,
                'description': 'Second trimester health check'
            },
            {
                'type': 'nutrition_change',
                'days': 150,
                'description': 'Adjust nutrition for late pregnancy'
            },
            {
                'type': 'trimester_start',
                'days': 190,
                'description': 'Third trimester begins'
            },
            {
                'type': 'health_check',
                'days': 210,
                'description': 'Third trimester health check'
            },
            {
                'type': 'preparation',
                'days': 260,
                'description': 'Begin calving preparation'
            },
        ]

        # Create milestones
        for milestone in milestones:
            due_date = self.last_insemination_date + timedelta(days=milestone['days'])
            if due_date >= timezone.now().date():
                GestationMilestone.objects.create(
                    cattle=self,
                    milestone_type=milestone['type'],
                    due_date=due_date,
                    description=milestone['description']
                )

    def save(self, *args, **kwargs):
        # Update gestation status and stage
        if self.last_insemination_date:
            days_pregnant = (timezone.now().date() - self.last_insemination_date).days
            if days_pregnant >= 0:
                self.gestation_status = 'pregnant'
                if days_pregnant <= 95:
                    self.gestation_stage = 'first_trimester'
                elif days_pregnant <= 190:
                    self.gestation_stage = 'second_trimester'
                elif days_pregnant <= 280:
                    self.gestation_stage = 'third_trimester'
                else:
                    self.gestation_stage = 'calving'
                    self.gestation_status = 'calving'
            
            # Calculate expected calving date
            self.expected_calving_date = self.last_insemination_date + timedelta(days=280)
        else:
            self.gestation_status = 'not_pregnant'
            self.gestation_stage = 'not_pregnant'
            self.expected_calving_date = None

        super().save(*args, **kwargs)

        # Generate milestones after save if pregnant
        if self.gestation_status == 'pregnant':
            self.generate_gestation_milestones()

    def get_milking_schedule(self):
        """Returns the milking schedule based on frequency or custom times"""
        if self.custom_milking_times:
            return self.custom_milking_times
        
        default_schedules = {
            'once': ['06:00'],
            'twice': ['06:00', '18:00'],
            'thrice': ['06:00', '14:00', '22:00']
        }
        return default_schedules.get(self.milking_frequency, ['06:00', '18:00'])

    def update_milking_frequency(self):
        """Updates milking frequency based on average daily production"""
        if self.avg_daily_milk > 25:  # High production
            self.milking_frequency = 'thrice'
        elif self.avg_daily_milk > 15:  # Medium production
            self.milking_frequency = 'twice'
        else:  # Low production
            self.milking_frequency = 'once'
        self.save()

    def can_record_milk(self):
        """Check if milk can be recorded for this cattle"""
        lactation_status = self.get_lactation_status()
        return (
            self.gender == 'female' and 
            lactation_status['status'] not in ['dry', 'not_lactating']
        )

    def get_next_milking_time(self):
        """Get the next available milking time"""
        from datetime import datetime
        current_time = datetime.now().strftime('%H:%M')
        schedule = self.get_milking_schedule()
        
        for time in schedule:
            if time > current_time:
                return time
        return schedule[0]  # Return first time of next day if all times passed

class TreatmentRecord(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='treatment_records')
    veterinarian = models.ForeignKey('userauth.User', on_delete=models.CASCADE, related_name='treatment_records')
    treatment_name = models.CharField(max_length=100)
    treatment_description = models.TextField(blank=True, null=True)
    treatment_date = models.DateField()
    treatment_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gestation_stage_target = models.CharField(
        max_length=20,
        choices=Cattle.GESTATION_STAGE_CHOICES,
        blank=True,
        null=True,
        help_text="Gestation stage for which this treatment is targeted, if applicable."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.treatment_name} for {self.cattle.ear_tag_no} - ({self.treatment_date})"

class VaccinationRecord(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='vaccination_records')
    veterinarian = models.ForeignKey('userauth.User', on_delete=models.CASCADE, related_name='vaccination_records')
    vaccination_name = models.CharField(max_length=100)
    vaccination_date = models.DateField()
    vaccination_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gestation_stage_target = models.CharField(
        max_length=20,
        choices=Cattle.GESTATION_STAGE_CHOICES,
        blank=True,
        null=True,
        help_text="Gestation stage for which this vaccination is targeted, if applicable."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vaccination_name} for {self.cattle.ear_tag_no} - ({self.vaccination_date})"

class PeriodicVaccinationRecord(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='periodic_vaccination_records', null=True, blank=True)
    veterinarian = models.ForeignKey('userauth.User', on_delete=models.CASCADE, related_name='periodic_vaccination_records')
    vaccination_name = models.CharField(max_length=100)
    last_vaccination_date = models.DateField()
    next_vaccination_date = models.DateField(blank=True, null=True)
    interval_days = models.PositiveIntegerField(help_text="Interval in days between vaccinations.")
    notification_sent = models.BooleanField(default=False)
    gestation_stage_target = models.CharField(
        max_length=20,
        choices=Cattle.GESTATION_STAGE_CHOICES,
        blank=True,
        null=True,
        help_text="Gestation stage for which this vaccination is targeted, if applicable."
    )
    vaccination_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_farm_wide = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.next_vaccination_date:
            self.next_vaccination_date = self.last_vaccination_date + timedelta(days=self.interval_days)
        super().save(*args, **kwargs)

    def is_due_for_vaccination(self):
        return timezone.now().date() >= self.next_vaccination_date

    def __str__(self):
        if self.is_farm_wide:
            return f"{self.vaccination_name} (Farm-wide) - (Next: {self.next_vaccination_date})"
        return f"{self.vaccination_name} for {self.cattle.ear_tag_no} - (Next: {self.next_vaccination_date})"

class PeriodicTreatmentRecord(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='periodic_treatment_records', null=True, blank=True)
    veterinarian = models.ForeignKey('userauth.User', on_delete=models.CASCADE, related_name='periodic_treatment_records')
    treatment_name = models.CharField(max_length=100)
    treatment_description = models.TextField(blank=True, null=True)
    last_treatment_date = models.DateField()
    next_treatment_date = models.DateField(blank=True, null=True)
    interval_days = models.PositiveIntegerField(help_text="Interval in days between treatments.")
    notification_sent = models.BooleanField(default=False)
    gestation_stage_target = models.CharField(
        max_length=20,
        choices=Cattle.GESTATION_STAGE_CHOICES,
        blank=True,
        null=True,
        help_text="Gestation stage for which this treatment is targeted, if applicable."
    )
    treatment_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_farm_wide = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.next_treatment_date:
            self.next_treatment_date = self.last_treatment_date + timedelta(days=self.interval_days)
        super().save(*args, **kwargs)

    def is_due_for_treatment(self):
        return timezone.now().date() >= self.next_treatment_date

    def __str__(self):
        if self.is_farm_wide:
            return f"{self.treatment_name} (Farm-wide) - (Next: {self.next_treatment_date})"
        return f"{self.treatment_name} for {self.cattle.ear_tag_no} - (Next: {self.next_treatment_date})"

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
    PREGNANCY_CHECK_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('negative', 'Negative'),
    ]
    insemination_method = models.CharField(max_length=50, choices=INSEMINATION_METHOD_CHOICES, default='natural')
    insemination_status = models.CharField(max_length=50, choices=INSEMINATION_STATUS_CHOICES, default='pending')
    insemination_date = models.DateField()
    pregnancy_check_date = models.DateField(null=True, blank=True)
    pregnancy_check_status = models.CharField(max_length=50, choices=PREGNANCY_CHECK_STATUS_CHOICES, default='pending')
    expected_calving_date = models.DateField(null=True, blank=True)
    pregnancy_check_reminder_sent = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Insemination for {self.cattle.ear_tag_no} on {self.insemination_date}"

    def create_pregnancy_check_alert(self):
        """Create an alert for pregnancy check (21 days after insemination)"""
        if not self.pregnancy_check_reminder_sent and self.insemination_date:
            check_date = self.insemination_date + timedelta(days=21)
            Alert.objects.create(
                cattle=self.cattle,
                message=f"Pregnancy check due for insemination performed on {self.insemination_date}",
                due_date=check_date,
                priority='High',
                alert_type='pregnancy_check'
            )
            self.pregnancy_check_reminder_sent = True
            self.save()

    def update_cattle_status(self):
        """Update cattle status based on pregnancy check results"""
        if not self.cattle:
            return

        if self.pregnancy_check_status == 'confirmed':
            # Update cattle status for confirmed pregnancy
            self.cattle.gestation_status = 'pregnant'
            self.cattle.gestation_stage = 'first_trimester'
            self.cattle.last_insemination_date = self.insemination_date
            self.cattle.expected_calving_date = self.expected_calving_date
            
            # Create alert for next vaccination/treatment if needed
            Alert.objects.create(
                cattle=self.cattle,
                title=f"Schedule first trimester check-up for {self.cattle.ear_tag_no}",
                description=f"First trimester check-up due for {self.cattle.ear_tag_no}",
                date=timezone.now(),
                type='reproduction',
                priority='Medium'
            )

        elif self.pregnancy_check_status == 'negative':
            # Update cattle status for failed pregnancy
            self.cattle.gestation_status = 'not_pregnant'
            self.cattle.gestation_stage = 'not_pregnant'
            self.cattle.expected_calving_date = None
            
            # Calculate next possible insemination date (21 days from negative check)
            next_insemination_date = timezone.now().date() + timedelta(days=21)
            self.cattle.expected_insemination_date = next_insemination_date
            
            # Create alert for next insemination
            Alert.objects.create(
                cattle=self.cattle,
                title=f"Schedule next insemination for {self.cattle.ear_tag_no}",
                description=f"Next insemination attempt due for {self.cattle.ear_tag_no}",
                date=timezone.now(),
                type='reproduction',
                priority='Medium'
            )

        self.cattle.save()

    def save(self, *args, **kwargs):
        # Calculate expected calving date (280 days from insemination)
        if self.insemination_date:
            self.expected_calving_date = self.insemination_date + timedelta(days=280)
        
        # Update insemination status based on pregnancy check
        if self.pregnancy_check_status == 'confirmed':
            self.insemination_status = 'successful'
        elif self.pregnancy_check_status == 'negative':
            self.insemination_status = 'failed'
        
        # Save the insemination record
        super().save(*args, **kwargs)
        
        # Update cattle status
        self.update_cattle_status()

class BirthRecord(models.Model):
    CALVING_OUTCOME_CHOICES = [
        ('successful', 'Successful'),
        ('complications', 'Complications'),
        ('stillborn', 'Stillborn'),
        ('died_shortly_after', 'Died Shortly After')
    ]
    
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='birth_records')
    calving_date = models.DateField()
    calving_outcome = models.CharField(max_length=50, choices=CALVING_OUTCOME_CHOICES)
    calf_count = models.PositiveIntegerField(default=1)
    calf_gender = models.CharField(max_length=50)
    calf_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    calf_ear_tag = models.CharField(max_length=100, unique=True, default='TEMP')
    complications = models.TextField(blank=True, null=True)
    veterinary_assistance = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Birth Record for {self.cattle.ear_tag_no} on {self.calving_date}"

    def register_calf(self):
        """Register a new calf in the system"""
        try:
            # Debug logging
            print(f"Registering new calf with ear tag: {self.calf_ear_tag}")
            print(f"Mother's ear tag: {self.cattle.ear_tag_no}")
            print(f"Mother's ID: {self.cattle.id}")
            
            # For multiple births, handle each calf
            ear_tags = [tag.strip() for tag in self.calf_ear_tag.split(',')]
            genders = [gender.strip().lower() for gender in self.calf_gender.split(',')]
            
            registered_calves = []
            for i, (ear_tag, gender) in enumerate(zip(ear_tags, genders)):
                print(f"Creating calf {i+1}: Tag={ear_tag}, Gender={gender}")
                
                calf = Cattle.objects.create(
                    ear_tag_no=ear_tag,
                    birth_date=self.calving_date,
                    gender=gender,
                    life_stage='calf',
                    dam_id=self.cattle.ear_tag_no,  # Set dam_id to mother's ear tag
                    breed=self.cattle.breed,  # Inherit breed from mother
                    farm=self.cattle.farm,
                    health_status='healthy',
                    gestation_status='open'
                )
                print(f"Successfully created calf: ID={calf.id}, Tag={calf.ear_tag_no}, Dam={calf.dam_id}")
                registered_calves.append(calf)
                
                # Create an alert for the new calf
                Alert.objects.create(
                    cattle=calf,
                    message=f"New calf registered with ear tag {ear_tag}. Born to {self.cattle.ear_tag_no}.",
                    due_date=self.calving_date,
                    priority='Low',
                    alert_type='general'
                )
            
            return registered_calves
        except Exception as e:
            print(f"Error registering calf: {str(e)}")
            raise

    def update_mother_status(self):
        """Update the mother's status after calving"""
        self.cattle.last_calving_date = self.calving_date
        self.cattle.gestation_status = 'not_pregnant'
        self.cattle.gestation_stage = 'not_pregnant'
        self.cattle.last_insemination_date = None
        self.cattle.expected_calving_date = None
        self.cattle.expected_insemination_date = self.calving_date + timedelta(days=60)  # Set next insemination date to 60 days after calving
        self.cattle.save()

    def create_health_alerts(self):
        """Create health-related alerts based on calving outcome"""
        alerts = []
        
        # Alert for successful calving
        alerts.append(Alert.objects.create(
            cattle=self.cattle,
            message=f"Successful calving recorded for {self.cattle.ear_tag_no}. Next insemination recommended after {self.cattle.expected_insemination_date}",
            due_date=self.cattle.expected_insemination_date,
            priority='Medium',
            alert_type='general'
        ))

        # Alert for complications
        if self.calving_outcome in ['complications', 'stillborn', 'died_shortly_after']:
            alerts.append(Alert.objects.create(
                cattle=self.cattle,
                message=f"Complications reported during calving for {self.cattle.ear_tag_no}. Veterinary attention required.",
                due_date=timezone.now().date(),
                priority='High',
                alert_type='general'
            ))

        # Alert for post-calving checkup
        alerts.append(Alert.objects.create(
            cattle=self.cattle,
            message=f"Schedule post-calving checkup for {self.cattle.ear_tag_no}",
            due_date=self.calving_date + timedelta(days=7),
            priority='High',
            alert_type='general'
        ))

        return alerts

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Check if this is a new record
        super().save(*args, **kwargs)
        
        if is_new:
            # Register the new calf if calving was successful
            if self.calving_outcome == 'successful':
                self.register_calf()
            
            # Update mother's status
            self.update_mother_status()
            
            # Create relevant alerts
            self.create_health_alerts()

class Alert(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    TYPE_CHOICES = [
        ('health', 'Health'),
        ('reproduction', 'Reproduction'),
        ('production', 'Production'),
        ('inventory', 'Inventory'),
        ('financial', 'Financial'),
        ('maintenance', 'Maintenance'),
    ]

    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='alerts')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='health')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')
    read = models.BooleanField(default=False)
    source_type = models.CharField(max_length=50, blank=True)  # e.g., 'treatment', 'vaccination', etc.
    source_id = models.CharField(max_length=50, blank=True)    # ID of the source record
    metadata = models.JSONField(null=True, blank=True)         # Additional data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.cattle.ear_tag_no} ({self.type})"

class GestationMilestone(models.Model):
    MILESTONE_TYPES = [
        ('health_check', 'Health Check'),
        ('vaccination', 'Vaccination'),
        ('nutrition_change', 'Nutrition Change'),
        ('trimester_start', 'Trimester Start'),
        ('preparation', 'Calving Preparation'),
    ]

    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='gestation_milestones')
    milestone_type = models.CharField(max_length=50, choices=MILESTONE_TYPES)
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.milestone_type} for {self.cattle.ear_tag_no} due on {self.due_date}"

    class Meta:
        ordering = ['due_date']

class GestationCheck(models.Model):
    HEALTH_STATUS_CHOICES = [
        ('normal', 'Normal'),
        ('attention', 'Needs Attention'),
        ('critical', 'Critical'),
    ]

    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='gestation_checks')
    check_date = models.DateField()
    gestation_week = models.PositiveIntegerField()
    health_status = models.CharField(max_length=20, choices=HEALTH_STATUS_CHOICES, default='normal')
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    body_condition_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    veterinarian = models.ForeignKey('userauth.User', on_delete=models.CASCADE, related_name='gestation_checks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Week {self.gestation_week} check for {self.cattle.ear_tag_no}"

    class Meta:
        ordering = ['-check_date']
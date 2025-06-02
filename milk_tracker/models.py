from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from core.models import Cattle, Farm
from django.db.models import Sum
from datetime import timedelta, date
from django.utils import timezone

#create model for milk tracking service

class Milk_record(models.Model):
    cattle_tag = models.ForeignKey(Cattle, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(default=date.today)
    time = models.TimeField(default=timezone.now)
    shift = models.CharField(max_length=20)
    ear_tag_no = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date', '-time']
        unique_together = ['cattle_tag', 'date', 'shift']

    def clean(self):
        if not self.cattle_tag.can_record_milk():
            raise ValidationError({
                'cattle_tag': 'Cannot record milk for this cattle - either dry or not lactating'
            })

        # Check if record already exists for this shift
        if Milk_record.objects.filter(
            cattle_tag=self.cattle_tag,
            date=self.date,
            shift=self.shift
        ).exclude(id=self.id).exists():
            raise ValidationError({
                'shift': f'Milk record already exists for {self.shift} shift on {self.date}'
            })

        # Validate shift against cattle's milking schedule
        schedule = self.cattle_tag.get_milking_schedule()
        current_time = self.time.strftime('%H:%M')
        
        # Find the closest scheduled time
        time_diffs = [(abs(int(t.split(':')[0]) - int(current_time.split(':')[0])), t) 
                     for t in schedule]
        closest_time = min(time_diffs, key=lambda x: x[0])[1]
        
        # If recording time is more than 2 hours from scheduled time, raise warning
        hour_diff = abs(int(closest_time.split(':')[0]) - int(current_time.split(':')[0]))
        if hour_diff > 2:
            raise ValidationError({
                'time': f'Recording time is too far from scheduled milking time {closest_time}'
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        # Update cattle's average daily production
        self.update_cattle_avg_production()

    def update_cattle_avg_production(self):
        """Update the cattle's average daily milk production"""
        last_30_days = now().date() - timedelta(days=30)
        daily_totals = Milk_record.objects.filter(
            cattle_tag=self.cattle_tag,
            date__gte=last_30_days
        ).values('date').annotate(
            daily_total=Sum('quantity')
        )
        
        if daily_totals:
            avg_production = sum(day['daily_total'] for day in daily_totals) / len(daily_totals)
            self.cattle_tag.avg_daily_milk = avg_production
            self.cattle_tag.update_milking_frequency()

    @classmethod
    def check_missing_records(cls, farm):
        """Check for missing milk records for lactating cattle"""
        today = now().date()
        alerts = []
        
        # Get all lactating cattle in the farm
        lactating_cattle = Cattle.objects.filter(
            farm=farm,
            gender='female'
        ).exclude(
            gestation_status__in=['dry_off', 'not_lactating']
        )
        
        for cattle in lactating_cattle:
            schedule = cattle.get_milking_schedule()
            current_time = now().time().strftime('%H:%M')
            
            # Check each scheduled time that has passed today
            for scheduled_time in schedule:
                if scheduled_time < current_time:
                    # Check if record exists
                    if not cls.objects.filter(
                        cattle_tag=cattle,
                        date=today,
                        time__hour=int(scheduled_time.split(':')[0])
                    ).exists():
                        alerts.append({
                            'cattle_tag': cattle.ear_tag_no,
                            'missed_time': scheduled_time,
                            'date': today
                        })
        
        return alerts

    def __str__(self):
        return f"{self.cattle_tag.ear_tag_no} - {self.date} {self.shift} - {self.quantity}L"
    






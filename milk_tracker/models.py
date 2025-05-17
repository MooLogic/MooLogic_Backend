from django.db import models
from core.models import Cattle

#create model for milk tracking service

class Milk_record(models.Model):
    cattle_tag = models.ForeignKey(Cattle, on_delete=models.CASCADE)
    ear_tag_no = models.CharField(max_length=20, null=True, blank=True)
    SHIFT_CHOICES = (
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('night', 'Night'),
    )
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    quantity = models.FloatField()


    def __str__(self):
        return f'{self.cattle_tag} - {self.date} - {self.quantity + " liters"}'
    






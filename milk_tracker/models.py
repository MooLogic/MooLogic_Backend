from django.db import models
from core.models import Cattle

#create model for milk tracking service

class Milk_record(models.Model):
    cattle_tag = models.ForeignKey(Cattle, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time= models.TimeField()
    quantity = models.FloatField()


    def __str__(self):
        return f'{self.cattle_tag} - {self.date} - {self.quantity + " liters"}'
    






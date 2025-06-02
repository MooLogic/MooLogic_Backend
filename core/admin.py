from django.contrib import admin
from .models import Cattle, Insemination, BirthRecord, Alert, Farm, TreatmentRecord, VaccinationRecord, PeriodicVaccinationRecord, PeriodicTreatmentRecord

admin.site.register(Cattle)
admin.site.register(Insemination)
admin.site.register(BirthRecord)
admin.site.register(Alert)
admin.site.register(Farm)
admin.site.register(TreatmentRecord)
admin.site.register(VaccinationRecord)
admin.site.register(PeriodicVaccinationRecord)
admin.site.register(PeriodicTreatmentRecord)    

# Register your models here.

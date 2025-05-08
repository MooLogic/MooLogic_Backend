from django.contrib import admin
from .models import Cattle, Insemination, BirthRecord, Alert, Farm

admin.site.register(Cattle)
admin.site.register(Insemination)
admin.site.register(BirthRecord)
admin.site.register(Alert)
admin.site.register(Farm)


# Register your models here.


from django.db import models

class Cattle(models.Model):
    breed = models.CharField(max_length=100,help_text="The breed of the cattle (e.g., Holstein, Jersey, Local).", blank=True, null=True)
    birth_date = models.DateField(help_text="The birth date of the cattle.", blank=True, null=True)
    ear_tag_no = models.CharField(max_length=100,help_text="The ear tag number of the cattle.")
    dam_id = models.CharField(max_length=100,help_text="The dam ID of the cattle.", blank=True, null=True)
    sire_id = models.CharField(max_length=100,help_text="The sire ID of the cattle.", blank=True, null=True)
    picture = models.ImageField(
        upload_to='cattle_pictures/',
        null=True,
        blank=True,
        help_text="An optional image of the cattle."
    )
    
    # Metadata (optional but useful for tracking)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    HEALTH_STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('sick', 'Sick'),
        ('recovering', 'Recovering'),
        ('unknown', 'Unknown'),
    ]
    health_status = models.CharField(
        max_length=20,
        choices=HEALTH_STATUS_CHOICES,
        default='unknown',
        help_text="The current health status of the cattle.",
        blank=True, 
        null=True
    )

    # Gender of the cattle
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        help_text="The gender of the cattle."
    )

    # Picture of the cattle (optional image field)
    

    class Meta:
        verbose_name = "Cattle"
        verbose_name_plural = "Cattle"

    def __str__(self):
        return f"Cattle {self.id} - {self.breed} ({self.gender})Ear Tag No:{self.earTagNo}"

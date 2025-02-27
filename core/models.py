
from django.db import models

class Cattle(models.Model):
    # ID is implicitly handled by Django as the primary key (AutoField) unless specified otherwise
    id = models.AutoField(primary_key=True)

    # Breed of the cattle
    breed = models.CharField(
        max_length=100,
        help_text="The breed of the cattle (e.g., Holstein, Jersey, Local)."
    )

    # Age of the cattle (assuming in months for precision, can be adjusted to years)
    age = models.PositiveIntegerField(
        help_text="The age of the cattle in months."
    )

    # Health status of the cattle
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
        help_text="The current health status of the cattle."
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
    picture = models.ImageField(
        upload_to='cattle_pictures/',
        null=True,
        blank=True,
        help_text="An optional image of the cattle."
    )
    earTagNo = models.CharField(
        max_length=50, blank=True, null=True)
    # Metadata (optional but useful for tracking)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cattle"
        verbose_name_plural = "Cattle"

    def __str__(self):
        return f"Cattle {self.id} - {self.breed} ({self.gender})Ear Tag No:{self.earTagNo}"

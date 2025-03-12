# Generated by Django 5.1 on 2025-03-12 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_cattle_expected_calving_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cattle',
            name='expected_insemination_date',
            field=models.DateField(blank=True, help_text='The expected inservation date of the cattle.', null=True),
        ),
    ]

# Generated by Django 5.1 on 2025-05-14 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('milk_tracker', '0003_milk_record_shift'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='milk_record',
            name='time',
        ),
    ]

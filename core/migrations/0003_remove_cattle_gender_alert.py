# Generated by Django 5.1 on 2025-03-06 07:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_cattle_gestation_status_cattle_last_calving_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cattle',
            name='gender',
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(help_text='The alert message.')),
                ('due_date', models.DateField(help_text='The date when the alert is due.')),
                ('is_read', models.BooleanField(default=False, help_text='Whether the alert has been read.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cattle', models.ForeignKey(help_text='The cattle associated with this alert.', on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='core.cattle')),
            ],
            options={
                'verbose_name': 'Alert',
                'verbose_name_plural': 'Alerts',
            },
        ),
    ]

# Generated by Django 5.1 on 2025-05-12 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0012_alter_user_worker_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('owner', 'Farm Owner'), ('manager', 'Farm Manager'), ('worker', 'Dairy Worker')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='worker_role',
            field=models.CharField(blank=True, choices=[('veterinary', 'Veterinary'), ('milktracker', 'Milk production tracker'), ('manager', 'Farm Manager'), ('finance', 'Finance'), ('generalpurpose', 'General Purpose')], default='generalpurpose', max_length=20, null=True),
        ),
    ]

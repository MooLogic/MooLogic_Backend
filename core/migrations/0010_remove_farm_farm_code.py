# Generated by Django 5.1 on 2025-05-09 07:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_farm_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='farm',
            name='farm_code',
        ),
    ]

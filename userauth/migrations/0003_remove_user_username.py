# Generated by Django 5.1 on 2025-02-18 10:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0002_alter_user_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]

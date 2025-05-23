# Generated by Django 4.2.20 on 2025-03-16 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0006_remove_user_farm_id_user_farm_alter_user_role'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='name',
            new_name='first_name',
        ),
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='user',
            name='get_email_notification',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='get_push_notification',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='get_sms_notification',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('am', 'Amharic'), ('or', 'Oromiffa')], default='en', max_length=2),
        ),
        migrations.AddField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='oversite_access',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=15),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('owner', 'Famr Owner'), ('manager', 'Farm Manager'), ('vaterinarian', 'Farm Veterinarian'), ('worker', 'Dairy Worker')], default='worker', max_length=20, null=True),
        ),
    ]

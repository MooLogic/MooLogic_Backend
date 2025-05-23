# Generated by Django 5.1.6 on 2025-03-22 08:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_alert_options_alter_cattle_options_and_more'),
        ('finance_tracker', '0003_remove_financialrecord_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomerecord',
            name='farm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.farm'),
        ),
        migrations.AlterField(
            model_name='profitsnapshot',
            name='farm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.farm'),
        ),
        migrations.AlterField(
            model_name='expenserecord',
            name='farm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.farm'),
        ),
        migrations.DeleteModel(
            name='Farm',
        ),
    ]

# Generated by Django 5.1.3 on 2025-03-23 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0007_employee_fullname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeetimesheet',
            name='hours_on_site',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]

# Generated by Django 5.1.3 on 2025-02-05 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0005_alter_employeetimesheet_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeetimesheet',
            name='check_in_time',
            field=models.DateTimeField(null=True),
        ),
    ]

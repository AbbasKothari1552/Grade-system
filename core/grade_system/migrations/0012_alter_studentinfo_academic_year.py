# Generated by Django 5.1.3 on 2024-12-29 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grade_system', '0011_studentinfo_academic_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentinfo',
            name='academic_year',
            field=models.CharField(max_length=9),
        ),
    ]

# Generated by Django 5.1.3 on 2024-11-14 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grade_system', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='subject_name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]

# Generated by Django 5.1.3 on 2024-12-18 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grade_system', '0008_alter_branchsubjectsemester_semester'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='result',
            field=models.CharField(choices=[('PASS', 'PASS'), ('FAIL', 'FAIL')], max_length=4),
        ),
    ]
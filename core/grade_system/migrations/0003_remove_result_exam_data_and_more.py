# Generated by Django 5.1.3 on 2024-11-14 16:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grade_system', '0002_alter_subject_subject_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='result',
            name='exam_data',
        ),
        migrations.AlterUniqueTogether(
            name='branchsubjectsemester',
            unique_together={('subject', 'branch', 'semester')},
        ),
    ]

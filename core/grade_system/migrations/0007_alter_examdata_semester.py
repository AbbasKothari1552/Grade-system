# Generated by Django 5.1.3 on 2024-12-18 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grade_system', '0006_alter_examdata_declaration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examdata',
            name='semester',
            field=models.CharField(max_length=12),
        ),
    ]

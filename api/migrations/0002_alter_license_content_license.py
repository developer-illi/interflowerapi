# Generated by Django 5.1.7 on 2025-05-29 05:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='license_content',
            name='license',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='license_certification', to='api.license'),
        ),
    ]

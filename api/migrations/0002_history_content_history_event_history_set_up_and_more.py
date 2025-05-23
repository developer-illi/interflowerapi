# Generated by Django 5.1.7 on 2025-04-03 10:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='History_content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='History_event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(default='content add', null=True)),
                ('img', models.ImageField(null=True, upload_to='history_img')),
                ('history_content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.history_content')),
            ],
        ),
        migrations.CreateModel(
            name='History_set_up',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dis_type', models.TextField(default='history', null=True)),
                ('title', models.TextField(default='2025')),
            ],
        ),
        migrations.DeleteModel(
            name='Association_history_month',
        ),
        migrations.DeleteModel(
            name='Association_history_year',
        ),
        migrations.AddField(
            model_name='history_content',
            name='history',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.history_set_up'),
        ),
    ]

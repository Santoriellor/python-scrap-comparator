# Generated by Django 4.2.13 on 2024-11-23 10:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('scrap', '0009_alter_search_query'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

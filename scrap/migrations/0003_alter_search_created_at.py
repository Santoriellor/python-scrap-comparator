# Generated by Django 5.0.4 on 2024-05-13 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrap', '0002_alter_search_result'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

# Generated by Django 5.0.4 on 2024-05-12 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrap', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='result',
            field=models.TextField(),
        ),
    ]

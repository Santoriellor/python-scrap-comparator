# Generated by Django 4.2.13 on 2024-11-18 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrap', '0007_product_delete_products_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='query',
            new_name='search',
        ),
        migrations.AlterField(
            model_name='product',
            name='img_src',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='img_srcset',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]

# Generated by Django 5.1.3 on 2024-11-29 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_alter_product_image_user_product_vendor_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='is_customer',
            field=models.BooleanField(default=False),
        ),
    ]

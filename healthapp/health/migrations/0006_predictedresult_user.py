# Generated by Django 4.2.19 on 2025-03-30 07:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('health', '0005_remove_ingredient_nutrient_nutrients_ingredient'),
    ]

    operations = [
        migrations.AddField(
            model_name='predictedresult',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

# Generated by Django 4.2.19 on 2025-03-28 12:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('health', '0003_dish_remove_meal_suggest_meal_suggest_dish'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nutrients',
            name='ingredient',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='nutrient',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='health.nutrients'),
        ),
    ]

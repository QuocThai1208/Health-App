# Generated by Django 4.2.19 on 2025-04-14 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health', '0014_alter_user_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='healthdiary',
            name='bmi',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='healthdiary',
            name='height',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='healthdiary',
            name='weight',
            field=models.FloatField(blank=True, default=0),
        ),
    ]

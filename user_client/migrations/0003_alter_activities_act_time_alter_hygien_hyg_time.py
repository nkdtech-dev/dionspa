# Generated by Django 4.2.2 on 2023-08-30 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_client', '0002_formula'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activities',
            name='act_time',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='hygien',
            name='hyg_time',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
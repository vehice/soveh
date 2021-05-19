# Generated by Django 2.0.3 on 2021-03-16 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0109_IdentificationCorrelative'),
    ]

    operations = [
        migrations.AddField(
            model_name='identification',
            name='client_case_number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='identification',
            name='quantity',
            field=models.IntegerField(blank=True, default='0', null=True),
        ),
        migrations.AddField(
            model_name='identification',
            name='samples_are_correlative',
            field=models.BooleanField(default=False),
        ),
    ]
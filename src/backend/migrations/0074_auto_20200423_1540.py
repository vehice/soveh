# Generated by Django 2.0.3 on 2020-04-23 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0073_remove_analysisform_closed_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='identification',
            name='organs_before_validations',
            field=models.ManyToManyField(related_name='organs_before_validations', to='backend.Organ'),
        ),
        migrations.AlterField(
            model_name='identification',
            name='organs',
            field=models.ManyToManyField(related_name='orgnas', to='backend.Organ'),
        ),
    ]

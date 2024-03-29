# Generated by Django 2.0.3 on 2018-06-08 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0018_cassette_identifications'),
    ]

    operations = [
        migrations.RenameField(
            model_name='slice',
            old_name='end_diagnostic',
            new_name='end_scan',
        ),
        migrations.RenameField(
            model_name='slice',
            old_name='start_diagnostic',
            new_name='end_stain',
        ),
        migrations.AddField(
            model_name='slice',
            name='start_scan',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='slice',
            name='start_stain',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

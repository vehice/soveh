# Generated by Django 2.0.3 on 2020-10-14 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0093_auto_20200929_0052'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entryform',
            name='research_type',
        ),
        migrations.AddField(
            model_name='analysisform',
            name='researches',
            field=models.ManyToManyField(to='backend.Research'),
        ),
    ]
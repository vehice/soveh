# Generated by Django 2.1.15 on 2021-08-10 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0124_auto_20210702_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='entryform',
            name='sampled_at_am_pm',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]

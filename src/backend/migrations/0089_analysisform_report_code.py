# Generated by Django 2.0.3 on 2020-08-30 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0088_auto_20200824_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysisform',
            name='report_code',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
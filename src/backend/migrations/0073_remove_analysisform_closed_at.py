# Generated by Django 2.0.3 on 2020-04-23 12:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0072_auto_20200416_1240'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analysisform',
            name='closed_at',
        ),
    ]

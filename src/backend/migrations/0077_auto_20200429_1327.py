# Generated by Django 2.0.3 on 2020-04-29 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0076_auto_20200429_1324'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cassette',
            old_name='sample',
            new_name='samples',
        ),
    ]
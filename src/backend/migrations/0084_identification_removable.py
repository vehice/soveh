# Generated by Django 2.0.3 on 2020-07-27 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0083_auto_20200727_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='identification',
            name='removable',
            field=models.BooleanField(default=False),
        ),
    ]

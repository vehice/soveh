# Generated by Django 2.0.3 on 2018-06-28 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0015_auto_20180607_1746'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='form_closed',
            field=models.BooleanField(default=False),
        ),
    ]

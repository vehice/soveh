# Generated by Django 2.0.3 on 2019-04-11 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0017_form_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='form_reopened',
            field=models.BooleanField(default=False),
        ),
    ]

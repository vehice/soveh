# Generated by Django 2.0.3 on 2020-04-07 12:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0065_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='service',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.Service'),
        ),
    ]

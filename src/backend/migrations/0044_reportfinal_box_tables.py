# Generated by Django 2.0.3 on 2019-01-07 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0043_reportfinal'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportfinal',
            name='box_tables',
            field=models.TextField(blank=True, null=True),
        ),
    ]

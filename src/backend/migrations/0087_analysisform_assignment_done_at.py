# Generated by Django 2.0.3 on 2020-08-20 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0086_auto_20200806_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysisform',
            name='assignment_done_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
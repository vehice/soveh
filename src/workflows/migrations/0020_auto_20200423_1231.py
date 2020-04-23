# Generated by Django 2.0.3 on 2020-04-23 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0019_DeleteCaso'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='cancelled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='form',
            name='cancelled_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='form',
            name='closed_at',
            field=models.DateTimeField(null=True),
        ),
    ]

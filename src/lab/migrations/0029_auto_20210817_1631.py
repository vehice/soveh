# Generated by Django 2.1.15 on 2021-08-17 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0028_unitdifference_status_change_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='slide',
            name='released_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='slide',
            name='build_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
# Generated by Django 2.0.3 on 2018-04-16 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_remove_entryform_flow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entryform',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

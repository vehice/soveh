# Generated by Django 2.1.15 on 2021-06-24 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0013_auto_20210624_1438'),
    ]

    operations = [
        migrations.RenameField(
            model_name='caseprocess',
            old_name='entryform',
            new_name='case',
        ),
    ]

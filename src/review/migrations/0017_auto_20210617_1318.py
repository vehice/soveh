# Generated by Django 2.1.15 on 2021-06-17 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0016_auto_20210610_1430'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='analysis',
            options={'permissions': (('send_email', 'Can send an email'),)},
        ),
    ]
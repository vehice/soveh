# Generated by Django 2.0.3 on 2020-07-28 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20181025_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_pathologist',
            field=models.BooleanField(default=False, verbose_name='¿Es patólogo?'),
        ),
    ]

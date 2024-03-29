# Generated by Django 2.1.15 on 2021-05-27 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0008_auto_20210527_1111'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maillist',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='recipient',
            name='deleted_at',
        ),
        migrations.AddField(
            model_name='maillist',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='recipient',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]

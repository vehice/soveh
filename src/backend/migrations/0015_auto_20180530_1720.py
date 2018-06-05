# Generated by Django 2.0.3 on 2018-05-30 21:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0014_auto_20180530_1605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cassette',
            name='slices',
        ),
        migrations.AddField(
            model_name='slice',
            name='analysis',
            field=models.ManyToManyField(to='backend.Analysis'),
        ),
        migrations.AddField(
            model_name='slice',
            name='cassettes',
            field=models.ManyToManyField(to='backend.Cassette'),
        ),
        migrations.AddField(
            model_name='slice',
            name='entryform',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.EntryForm'),
        ),
    ]

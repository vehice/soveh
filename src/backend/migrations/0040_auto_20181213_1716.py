# Generated by Django 2.0.3 on 2018-12-13 20:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0039_auto_20181212_2003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='slice',
            name='cassettes',
        ),
        migrations.AddField(
            model_name='slice',
            name='cassette',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.Cassette'),
        ),
        migrations.RemoveField(
            model_name='slice',
            name='analysis',
        ),
        migrations.AddField(
            model_name='slice',
            name='analysis',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.AnalysisForm'),
        ),
    ]

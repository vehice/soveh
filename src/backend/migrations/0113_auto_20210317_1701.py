# Generated by Django 2.0.3 on 2021-03-17 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0112_auto_20210317_0850'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organ', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Organ')),
            ],
        ),
        migrations.RemoveField(
            model_name='unit',
            name='organs',
        ),
        migrations.AddField(
            model_name='organunit',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Unit'),
        ),
    ]
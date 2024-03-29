# Generated by Django 2.0.3 on 2021-01-15 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0103_analysisform_manual_cancelled_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='research',
            name='clients',
            field=models.ManyToManyField(to='backend.Customer', verbose_name='Clientes'),
        ),
        migrations.AddField(
            model_name='research',
            name='init_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='research',
            name='responsible',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='research',
            name='services',
            field=models.ManyToManyField(to='backend.AnalysisForm', verbose_name='Servicios Asociados'),
        ),
        migrations.AddField(
            model_name='research',
            name='type',
            field=models.IntegerField(choices=[(1, 'Estudio Vehice'), (2, 'Seguimiento de rutina')], default=1, verbose_name='Tipo'),
        ),
    ]

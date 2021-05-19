# Generated by Django 2.1.15 on 2021-05-06 11:24

import backend.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0117_auto_20210321_2141'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': 'cliente'},
        ),
        migrations.AlterModelOptions(
            name='diagnostic',
            options={'verbose_name': 'diagnóstico', 'verbose_name_plural': 'diagnósticos'},
        ),
        migrations.AlterModelOptions(
            name='emailccto',
            options={'verbose_name': 'destinatario copiado en Plantilla Email', 'verbose_name_plural': 'destinatarios copiados en Plantilla Email'},
        ),
        migrations.AlterModelOptions(
            name='emailtemplateattachment',
            options={'verbose_name': 'email Adjunto', 'verbose_name_plural': 'email Adjuntos'},
        ),
        migrations.AlterModelOptions(
            name='entryform_type',
            options={'verbose_name': 'tipo de Ingreso', 'verbose_name_plural': 'tipos de Ingreso'},
        ),
        migrations.AlterModelOptions(
            name='exam',
            options={'verbose_name': 'exámen', 'verbose_name_plural': 'exámenes'},
        ),
        migrations.AlterModelOptions(
            name='fixative',
            options={'verbose_name': 'fijador', 'verbose_name_plural': 'fijadores'},
        ),
        migrations.AlterModelOptions(
            name='organ',
            options={'verbose_name': 'órgano', 'verbose_name_plural': 'órganos'},
        ),
        migrations.AlterModelOptions(
            name='organlocation',
            options={'verbose_name': 'localización', 'verbose_name_plural': 'localizaciones'},
        ),
        migrations.AlterModelOptions(
            name='research',
            options={'verbose_name': 'estudio', 'verbose_name_plural': 'estudios'},
        ),
        migrations.AlterModelOptions(
            name='responsible',
            options={'verbose_name': 'responsable', 'verbose_name_plural': 'responsables'},
        ),
        migrations.AlterModelOptions(
            name='service',
            options={'verbose_name': 'servicio', 'verbose_name_plural': 'servicios'},
        ),
        migrations.AlterModelOptions(
            name='stain',
            options={'verbose_name': 'tinción', 'verbose_name_plural': 'tinciones'},
        ),
        migrations.AlterField(
            model_name='analysisform',
            name='stain',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.Stain', verbose_name='tinción'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='company',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='empresa'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='diagnostic',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='nombre del diagnóstico'),
        ),
        migrations.AlterField(
            model_name='diagnostic',
            name='organs',
            field=models.ManyToManyField(to='backend.Organ', verbose_name='órganos'),
        ),
        migrations.AlterField(
            model_name='emailccto',
            name='email',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='correo Electrónico'),
        ),
        migrations.AlterField(
            model_name='emailtemplateattachment',
            name='template_file',
            field=models.FileField(upload_to=backend.models.entry_files_directory_path, verbose_name='archivo Adjunto'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='pathologists_assignment',
            field=models.BooleanField(default=True, verbose_name='asignación de patólogo'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='pricing_unit',
            field=models.IntegerField(choices=[(1, 'Por órgano'), (2, 'Por pez')], default=1, verbose_name='unidad de cobro'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='service',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.Service', verbose_name='tipo de Servicio'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='stain',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.Stain', verbose_name='tinción'),
        ),
        migrations.AlterField(
            model_name='fixative',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='organ',
            name='abbreviation',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='abreviatura (ESP)'),
        ),
        migrations.AlterField(
            model_name='organ',
            name='abbreviation_en',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='abreviatura (EN)'),
        ),
        migrations.AlterField(
            model_name='organ',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='nombre (ESP)'),
        ),
        migrations.AlterField(
            model_name='organ',
            name='name_en',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='nombre (EN)'),
        ),
        migrations.AlterField(
            model_name='organ',
            name='organ_type',
            field=models.IntegerField(choices=[(1, 'Órgano por sí solo'), (2, 'Conjunto de órganos')], default=1, verbose_name='tipo'),
        ),
        migrations.AlterField(
            model_name='organlocation',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='nombre de localización'),
        ),
        migrations.AlterField(
            model_name='organlocation',
            name='organs',
            field=models.ManyToManyField(to='backend.Organ', verbose_name='órganos'),
        ),
        migrations.AlterField(
            model_name='research',
            name='clients',
            field=models.ManyToManyField(to='backend.Customer', verbose_name='clientes'),
        ),
        migrations.AlterField(
            model_name='research',
            name='code',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='código'),
        ),
        migrations.AlterField(
            model_name='research',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='descripción'),
        ),
        migrations.AlterField(
            model_name='research',
            name='external_responsible',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='responsable externo'),
        ),
        migrations.AlterField(
            model_name='research',
            name='internal_responsible',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='responsable interno'),
        ),
        migrations.AlterField(
            model_name='research',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='research',
            name='services',
            field=models.ManyToManyField(to='backend.AnalysisForm', verbose_name='servicios Asociados'),
        ),
        migrations.AlterField(
            model_name='research',
            name='status',
            field=models.BooleanField(default=False, verbose_name='¿activo?'),
        ),
        migrations.AlterField(
            model_name='research',
            name='type',
            field=models.IntegerField(choices=[(1, 'Estudio Vehice'), (2, 'Seguimiento de rutina')], default=1, verbose_name='tipo'),
        ),
        migrations.AlterField(
            model_name='sampleexams',
            name='stain',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.Stain', verbose_name='tinción'),
        ),
        migrations.AlterField(
            model_name='service',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='stain',
            name='abbreviation',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='abreviación'),
        ),
        migrations.AlterField(
            model_name='stain',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='descripción'),
        ),
        migrations.AlterField(
            model_name='stain',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='nombre'),
        ),
    ]
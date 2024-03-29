# Generated by Django 2.1.15 on 2021-06-29 10:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0123_sampleexams_unit_organ'),
        ('lab', '0015_auto_20210629_1054'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='processunit',
            name='completed',
        ),
        migrations.AddField(
            model_name='processunit',
            name='unit',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='processes', to='backend.Unit'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='processunit',
            name='case_process',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='process_units', to='lab.CaseProcess'),
        ),
    ]

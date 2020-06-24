# Generated by Django 2.0.3 on 2020-06-19 13:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backend', '0080_entryform_entryform_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='vehice_case_files')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('loaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='entryform',
            name='attached_files',
            field=models.ManyToManyField(to='backend.CaseFile'),
        ),
    ]
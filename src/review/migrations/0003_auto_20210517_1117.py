# Generated by Django 2.1.15 on 2021-05-17 11:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('review', '0002_auto_20210513_1129'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.FileField(upload_to='', verbose_name='reviews/%Y_%m_%d/')),
                ('state', models.CharField(choices=[(0, 'ESPERA'), (1, 'FORMATO'), (2, 'REVISION'), (3, 'ENVIO'), (4, 'FINALIZADO')], max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='review.Analysis')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='logbook',
            name='state',
            field=models.CharField(choices=[(0, 'ESPERA'), (1, 'FORMATO'), (2, 'REVISION'), (3, 'ENVIO'), (4, 'FINALIZADO')], max_length=1),
        ),
        migrations.AlterField(
            model_name='stage',
            name='state',
            field=models.CharField(choices=[(0, 'ESPERA'), (1, 'FORMATO'), (2, 'REVISION'), (3, 'ENVIO'), (4, 'FINALIZADO')], default=0, max_length=1),
        ),
    ]

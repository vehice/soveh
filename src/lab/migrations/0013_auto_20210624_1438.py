# Generated by Django 2.1.15 on 2021-06-24 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0012_auto_20210624_1314'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField()),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('completed', models.BooleanField(verbose_name='finalizado')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('case_process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='process_items', to='lab.CaseProcess')),
            ],
        ),
        migrations.AlterModelOptions(
            name='process',
            options={'verbose_name_plural': 'processes'},
        ),
    ]

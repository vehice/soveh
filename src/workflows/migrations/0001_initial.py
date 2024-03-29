# Generated by Django 2.0.3 on 2018-04-02 20:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Flow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('name', models.CharField(blank=True, max_length=250, null=True)),
                ('state', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='workflows.State')),
                ('actors', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='workflows.Actor')),
            ],
        ),
        migrations.AddField(
            model_name='flow',
            name='state',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='workflows.State'),
        ),
        migrations.AddField(
            model_name='step',
            name='flow',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='workflows.Flow'),
        ),
    ]

# Generated by Django 2.1.15 on 2021-05-06 11:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('backend', '0118_auto_20210506_1124'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cassette',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correlative', models.PositiveIntegerField()),
                ('build_at', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organs', models.ManyToManyField(related_name='cassettes', to='backend.Organ')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cassettes', to='backend.Unit')),
            ],
        ),
        migrations.CreateModel(
            name='Slide',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correlative', models.PositiveIntegerField()),
                ('build_at', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cassette', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='slides', to='lab.Cassette')),
                ('stain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slides', to='backend.Stain')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slides', to='backend.Unit')),
            ],
        ),
        migrations.CreateModel(
            name='Case',
            fields=[
            ],
            options={
                'ordering': ['-entryform_type_id', '-created_at'],
                'proxy': True,
                'indexes': [],
            },
            bases=('backend.entryform',),
        ),
    ]

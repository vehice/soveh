# Generated by Django 2.1.15 on 2021-06-24 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0118_auto_20210506_1124'),
        ('lab', '0011_tree_process'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseProcess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('entryform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='case_process', to='backend.EntryForm')),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='case_process', to='lab.Process')),
            ],
        ),
        migrations.CreateModel(
            name='ExamTree',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_trees', to='backend.Exam')),
                ('tree', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_trees', to='lab.Tree')),
            ],
        ),
        migrations.AddField(
            model_name='process',
            name='case',
            field=models.ManyToManyField(related_name='processes', through='lab.CaseProcess', to='backend.EntryForm'),
        ),
    ]
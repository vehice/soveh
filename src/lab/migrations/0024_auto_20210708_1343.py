# Generated by Django 2.1.15 on 2021-07-08 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0023_auto_20210707_1443'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tree',
            name='entry_type',
        ),
        migrations.AddField(
            model_name='tree',
            name='entry_format',
            field=models.IntegerField(blank=True, choices=[(1, 'Tubo'), (2, 'Cassette'), (3, 'Bloque'), (4, 'Slide s/teñir'), (5, 'Slide teñido'), (6, 'Vivo'), (7, 'Muerto')], null=True),
        ),
    ]
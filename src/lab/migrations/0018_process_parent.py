# Generated by Django 2.1.15 on 2021-07-05 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0017_caseprocess_deleted_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='lab.Process'),
        ),
    ]

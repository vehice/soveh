# Generated by Django 2.0.3 on 2018-06-29 16:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0016_form_form_closed'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='workflows.Form'),
        ),
    ]

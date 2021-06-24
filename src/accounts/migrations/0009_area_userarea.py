# Generated by Django 2.1.15 on 2021-06-10 14:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0008_userprofile_is_reviewer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('is_deleted', models.SmallIntegerField(default=0, verbose_name='desactivado')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.SmallIntegerField(choices=[(0, 'jefe'), (1, 'miembro')], default=(1, 'miembro'), verbose_name='rol')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='accounts.Area')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='areas', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
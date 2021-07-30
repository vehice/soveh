# Generated by Django 2.1.15 on 2021-07-20 11:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0017_auto_20210617_1318'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisRecipient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_main', models.BooleanField(default=True, verbose_name='Is primary recipient (TO)')),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='review.Analysis')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='review.Recipient')),
            ],
        ),
        migrations.RemoveField(
            model_name='analysismaillist',
            name='analysis',
        ),
        migrations.RemoveField(
            model_name='analysismaillist',
            name='mail_list',
        ),
        migrations.RemoveField(
            model_name='maillist',
            name='analysis',
        ),
        migrations.DeleteModel(
            name='AnalysisMailList',
        ),
    ]
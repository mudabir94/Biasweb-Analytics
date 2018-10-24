# Generated by Django 2.1.2 on 2018-10-24 14:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0036_auto_20181021_1507'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='experiment',
            name='admin',
            field=models.ManyToManyField(related_name='can_modify', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='experiment',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='creator', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.RenameModel(
            old_name='Experiment_Batch',
            new_name='Batch',
        ),
        migrations.AddField(
            model_name='subject',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webapp.Batch'),
        ),
        migrations.AddField(
            model_name='subject',
            name='block',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webapp.Block'),
        ),
        migrations.AddField(
            model_name='subject',
            name='exp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.experiment'),
        ),
        migrations.AddField(
            model_name='subject',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

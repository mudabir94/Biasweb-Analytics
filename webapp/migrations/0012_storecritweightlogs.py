# Generated by Django 2.0.5 on 2019-08-16 09:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0011_storehoverbarchartlogs_storehoverpiechartlogs_storenextprevbuttonlogs'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreCritWeightLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(blank=True, null=True)),
                ('criteria_name', models.CharField(blank=True, max_length=45, null=True)),
                ('time', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

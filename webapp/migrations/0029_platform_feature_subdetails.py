# Generated by Django 2.0.5 on 2018-10-15 11:56

from django.db import migrations, models
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0028_auto_20181011_0031'),
    ]

    operations = [
        migrations.AddField(
            model_name='platform_feature',
            name='subdetails',
            field=django_mysql.models.ListCharField(models.CharField(max_length=10), blank=True, max_length=66, null=True, size=6),
        ),
    ]

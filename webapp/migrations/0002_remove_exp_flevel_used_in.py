# Generated by Django 2.1.2 on 2018-11-01 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exp_flevel',
            name='used_in',
        ),
    ]

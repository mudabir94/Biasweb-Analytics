# Generated by Django 2.1.2 on 2018-10-25 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0041_auto_20181025_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='block',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webapp.Block'),
        ),
    ]
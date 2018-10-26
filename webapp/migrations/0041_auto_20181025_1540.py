# Generated by Django 2.1.2 on 2018-10-25 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0040_auto_20181025_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='batch',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='block',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webapp.Block'),
        ),
    ]
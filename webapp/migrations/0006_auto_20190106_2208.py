# Generated by Django 2.0.5 on 2019-01-07 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0005_auto_20181231_0519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phone',
            name='imagepath1',
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='phone',
            name='imagepath2',
            field=models.CharField(max_length=300, null=True),
        ),
    ]
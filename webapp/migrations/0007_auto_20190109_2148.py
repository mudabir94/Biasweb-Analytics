# Generated by Django 2.0.5 on 2019-01-10 05:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0006_auto_20190106_2208'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='phone',
            new_name='mobilephones',
        ),
        migrations.AlterModelOptions(
            name='mobilephones',
            options={'verbose_name_plural': 'mobilephones'},
        ),
    ]

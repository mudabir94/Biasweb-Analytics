# Generated by Django 2.0.5 on 2018-10-06 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0023_auto_20181006_0542'),
    ]

    operations = [
        migrations.CreateModel(
            name='experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('experiment_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'experiment',
                'ordering': ['pk'],
            },
        ),
        migrations.AlterModelOptions(
            name='platform_feature',
            options={'ordering': ['pk'], 'verbose_name_plural': 'platform_feature'},
        ),
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ['pk'], 'verbose_name_plural': 'Role'},
        ),
    ]

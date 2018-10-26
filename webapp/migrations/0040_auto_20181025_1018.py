# Generated by Django 2.1.2 on 2018-10-25 05:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0039_auto_20181024_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='status',
            field=models.CharField(default='DESIGN_MODE', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='subject',
            name='block',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webapp.Block'),
        ),
    ]
# Generated by Django 2.0.5 on 2018-12-31 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0004_selectedadminphones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sort_feature',
            name='roles',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.Role'),
        ),
    ]

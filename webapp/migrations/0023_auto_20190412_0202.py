# Generated by Django 2.0.5 on 2019-04-12 09:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0022_expcriteriaorder_fvp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expcriteriaorder',
            name='pCriteria',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.PhoneCriteria'),
        ),
    ]

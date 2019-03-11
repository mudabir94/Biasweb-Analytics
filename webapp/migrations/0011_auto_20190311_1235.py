# Generated by Django 2.1.2 on 2019-03-11 07:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0010_auto_20190212_0536'),
    ]

    operations = [
        migrations.AddField(
            model_name='selectedadminphones',
            name='block',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.Block'),
        ),
        migrations.AddField(
            model_name='selectedadminphones',
            name='p_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='selectedadminphones',
            name='pset_id',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='selectedadminphones',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

# Generated by Django 2.0.5 on 2019-10-31 13:27

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_mysql.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_student', models.BooleanField(default=False)),
                ('is_prof', models.BooleanField(default=False)),
                ('is_ra', models.BooleanField(default=False)),
                ('platform_admin', models.BooleanField(default=False)),
                ('experiment_admin', models.BooleanField(default=False)),
                ('custom_id', models.CharField(blank=True, default=None, max_length=100, null=True, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_label', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_no', models.IntegerField()),
                ('levels_set', django_mysql.models.ListCharField(models.CharField(max_length=20), max_length=210, size=10)),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='blog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': 'Blog',
            },
        ),
        migrations.CreateModel(
            name='criteria_catalog_disp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catalog_crit_display_order', django_mysql.models.ListCharField(models.CharField(max_length=20), max_length=210, null=True, size=10)),
            ],
        ),
        migrations.CreateModel(
            name='customExpSessionTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expid', models.IntegerField(blank=True, null=True)),
                ('cusexpid', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='exp_fdefaults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_level', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name_plural': 'Exp Default Feature',
            },
        ),
        migrations.CreateModel(
            name='exp_fLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chosen_level', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ExpCriteriaOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cOrder_id', models.CharField(max_length=10, null=True)),
                ('fvp', models.CharField(max_length=25, null=True)),
                ('position', models.IntegerField(null=True)),
                ('sh_hd', models.IntegerField(null=True)),
                ('block', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.Block')),
            ],
        ),
        migrations.CreateModel(
            name='experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='DESIGN_MODE', max_length=100)),
                ('custom_exp_id', models.CharField(blank=True, max_length=100, null=True)),
                ('batches_title', models.CharField(blank=True, max_length=100, null=True)),
                ('capacity', models.IntegerField(blank=True, default=100, null=True)),
                ('inFile', models.CharField(blank=True, max_length=256, null=True)),
                ('outFile', models.CharField(blank=True, max_length=256, null=True)),
                ('desc', models.CharField(blank=True, max_length=256, null=True)),
                ('admin', models.ManyToManyField(related_name='can_modify', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='creator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'experiment',
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='experiment_feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chosen_levels', django_mysql.models.ListCharField(models.CharField(max_length=20), blank=True, max_length=126, null=True, size=6)),
                ('default_levels', django_mysql.models.ListCharField(models.CharField(max_length=20), blank=True, max_length=126, null=True, size=6)),
            ],
        ),
        migrations.CreateModel(
            name='exStatusCd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_name', models.CharField(blank=True, max_length=100, null=True)),
                ('status_code', models.IntegerField()),
                ('s_description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'ExpStatusCode',
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='generalCriteriaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valuelist', django_mysql.models.ListCharField(models.CharField(max_length=20), blank=True, max_length=210, null=True, size=10)),
                ('inputtype', models.CharField(default='-', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='mobilephones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Brand', models.CharField(max_length=200, null=True)),
                ('Mobile_Name', models.CharField(max_length=300, null=True)),
                ('Whats_new', models.TextField(null=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('Memory', models.CharField(blank=True, max_length=500, null=True)),
                ('Ram', models.CharField(blank=True, max_length=500, null=True)),
                ('Cpu', models.CharField(max_length=500, null=True)),
                ('Dimensions', models.CharField(max_length=300, null=True)),
                ('Gpu', models.CharField(max_length=500, null=True)),
                ('Resolution', models.CharField(max_length=500, null=True)),
                ('Size', models.FloatField(null=True)),
                ('Weight', models.IntegerField(null=True)),
                ('Chip', models.CharField(max_length=500, null=True)),
                ('Colors', models.CharField(max_length=300, null=True)),
                ('price_in_usd', models.IntegerField(null=True)),
                ('rating', models.FloatField(null=True)),
                ('OS', models.CharField(max_length=300, null=True)),
                ('imagepath1', models.CharField(blank=True, max_length=300, null=True)),
                ('sideimage1', models.CharField(blank=True, max_length=300, null=True)),
                ('sideimage2', models.CharField(blank=True, max_length=300, null=True)),
                ('sideimage3', models.CharField(blank=True, max_length=300, null=True)),
                ('sideimage4', models.CharField(blank=True, max_length=300, null=True)),
                ('battery', models.CharField(max_length=400, null=True)),
                ('backcam', models.CharField(max_length=400, null=True)),
            ],
            options={
                'verbose_name_plural': 'mobilephones',
            },
        ),
        migrations.CreateModel(
            name='MobilePhones_Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Mobile_Companny', models.CharField(max_length=200, null=True)),
                ('Mobile_Name', models.CharField(max_length=300, null=True)),
                ('Whats_new', models.TextField(null=True)),
                ('price', models.IntegerField(null=True)),
                ('battery', models.CharField(max_length=400, null=True)),
                ('Cpu', models.CharField(max_length=500, null=True)),
                ('Dimensions', models.CharField(max_length=300, null=True)),
                ('Gpu', models.CharField(max_length=500, null=True)),
                ('Resolution', models.CharField(max_length=500, null=True)),
                ('Size', models.FloatField(null=True)),
                ('Weight', models.IntegerField(null=True)),
                ('Chip', models.CharField(max_length=500, null=True)),
                ('Colors', models.CharField(max_length=300, null=True)),
                ('price_in_usd', models.IntegerField(null=True)),
                ('rating', models.FloatField(null=True)),
                ('OS', models.CharField(max_length=300, null=True)),
                ('imagepath1', models.CharField(max_length=300, null=True)),
                ('imagepath2', models.CharField(max_length=300, null=True)),
                ('backcam', models.CharField(max_length=400, null=True)),
            ],
            options={
                'verbose_name_plural': 'Mobile Phones Test',
            },
        ),
        migrations.CreateModel(
            name='PhoneCriteria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criteria_name', models.CharField(max_length=20, null=True)),
                ('status', models.CharField(max_length=20, null=True)),
                ('priority', models.CharField(max_length=20, null=True)),
                ('position', models.IntegerField(null=True)),
            ],
            options={
                'verbose_name_plural': 'Phone Criteria',
            },
        ),
        migrations.CreateModel(
            name='platform_feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_name', models.CharField(blank=True, max_length=100, null=True)),
                ('feature_symbol', models.CharField(max_length=3, null=True)),
                ('feature_levels', django_mysql.models.ListCharField(models.CharField(max_length=20), blank=True, max_length=126, null=True, size=6)),
                ('default_levels', django_mysql.models.ListCharField(models.CharField(max_length=20), blank=True, max_length=126, null=True, size=6)),
            ],
            options={
                'verbose_name_plural': 'platform_feature',
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(max_length=45)),
            ],
            options={
                'verbose_name_plural': 'Role',
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='samsung_phone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Mobile_Companny', models.CharField(max_length=200, null=True)),
                ('Mobile_Name', models.CharField(max_length=300, null=True)),
                ('Whats_new', models.TextField(null=True)),
                ('Chip', models.CharField(max_length=500, null=True)),
                ('Colors', models.CharField(max_length=300, null=True)),
                ('Cpu', models.CharField(max_length=500, null=True)),
                ('Dimensions', models.CharField(max_length=300, null=True)),
                ('Gpu', models.CharField(max_length=500, null=True)),
                ('Resolution', models.CharField(max_length=500, null=True)),
                ('Size', models.FloatField(null=True)),
                ('Weight', models.IntegerField(null=True)),
                ('price_in_pkr', models.IntegerField(null=True)),
                ('price_in_usd', models.IntegerField(null=True)),
                ('rating', models.FloatField(null=True)),
                ('OS', models.CharField(max_length=300, null=True)),
                ('imagepath1', models.CharField(max_length=300, null=True)),
                ('imagepath2', models.CharField(max_length=300, null=True)),
                ('battery', models.CharField(max_length=400, null=True)),
                ('back_camera', models.CharField(max_length=400, null=True)),
            ],
            options={
                'verbose_name_plural': 'samsungphone',
            },
        ),
        migrations.CreateModel(
            name='selectedAdminPhones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pset_id', models.CharField(blank=True, max_length=10, null=True)),
                ('p_order', models.IntegerField(blank=True, null=True)),
                ('block', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.Block')),
                ('exp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.experiment')),
                ('mob', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.mobilephones')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='signup_table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=300, null=True)),
                ('role', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='sort_feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f_id', models.IntegerField(null=True)),
                ('feature', models.CharField(max_length=200, null=True)),
                ('position', models.IntegerField(null=True)),
                ('sh_hd', models.IntegerField(null=True)),
                ('exp_sets', models.CharField(max_length=200, null=True)),
                ('roles', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.Role')),
            ],
            options={
                'verbose_name_plural': 'Sort Feature',
            },
        ),
        migrations.CreateModel(
            name='StoreCritWeightLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(blank=True, null=True)),
                ('criteria_name', models.CharField(blank=True, max_length=45, null=True)),
                ('time', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StoreHoverBarChartLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(blank=True, null=True)),
                ('phone_name', models.CharField(blank=True, max_length=45, null=True)),
                ('time', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StoreHoverPieChartLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(blank=True, null=True)),
                ('criteria_name', models.CharField(blank=True, max_length=45, null=True)),
                ('time', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StoreNextPrevButtonLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('button_name', models.CharField(blank=True, max_length=45, null=True)),
                ('time', models.CharField(blank=True, max_length=100, null=True)),
                ('phone_name', models.CharField(blank=True, max_length=45, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(max_length=100)),
                ('block', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webapp.Block')),
                ('exp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.experiment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='surveyForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('surveydata', django_mysql.models.ListCharField(models.CharField(max_length=30), blank=True, max_length=400, null=True, size=10)),
                ('exp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.experiment')),
            ],
        ),
        migrations.CreateModel(
            name='userroles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userrole', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='userscoreRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('column_id', models.IntegerField(null=True)),
                ('element_id', models.IntegerField(null=True)),
                ('feat_priority', models.IntegerField(null=True)),
                ('feat_name', models.CharField(max_length=200, null=True)),
                ('mobile_id', models.IntegerField(null=True)),
                ('user_id', models.IntegerField(null=True)),
                ('date_created', models.DateField(default=datetime.date.today, verbose_name='Date')),
                ('date_modified', models.DateField(default=datetime.date.today, verbose_name='Date')),
            ],
            options={
                'verbose_name_plural': 'User Score Record',
            },
        ),
        migrations.AddField(
            model_name='generalcriteriadata',
            name='criteria',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.PhoneCriteria'),
        ),
        migrations.AddField(
            model_name='experiment_feature',
            name='p_feature',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.platform_feature'),
        ),
        migrations.AddField(
            model_name='experiment_feature',
            name='used_in',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.experiment'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='status_code',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='webapp.exStatusCd'),
        ),
        migrations.AddField(
            model_name='expcriteriaorder',
            name='exp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.experiment'),
        ),
        migrations.AddField(
            model_name='expcriteriaorder',
            name='pCriteria',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.PhoneCriteria'),
        ),
        migrations.AddField(
            model_name='exp_flevel',
            name='e_feature',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.experiment_feature'),
        ),
        migrations.AddField(
            model_name='exp_flevel',
            name='used_in',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.experiment'),
        ),
        migrations.AddField(
            model_name='exp_fdefaults',
            name='d_feature',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.platform_feature'),
        ),
        migrations.AddField(
            model_name='exp_fdefaults',
            name='used_in',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.experiment'),
        ),
        migrations.AddField(
            model_name='block',
            name='used_in',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.experiment'),
        ),
        migrations.AddField(
            model_name='batch',
            name='exp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.experiment'),
        ),
        migrations.AddField(
            model_name='user',
            name='role_id',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.Role'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]

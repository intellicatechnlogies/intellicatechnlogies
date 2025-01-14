# Generated by Django 5.1.3 on 2025-01-14 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='apiUser',
            fields=[
                ('sno', models.AutoField(primary_key=True, serialize=False)),
                ('api_key', models.CharField(default='ABCDWXYZ', max_length=36)),
                ('app_id', models.CharField(default='ABCDWXYZ', max_length=36)),
                ('client', models.CharField(default='Intellica Technologies Pvt Ltd', max_length=50)),
                ('platform', models.CharField(default='ABCDWXYZ', max_length=36)),
                ('usage_quota', models.IntegerField(default=500)),
                ('assigned_api', models.JSONField(default=dict)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='transactions_log',
            fields=[
                ('sno', models.AutoField(primary_key=True, serialize=False)),
                ('api_key', models.CharField(default='ABCDWXYZ', max_length=36)),
                ('service', models.CharField(default='ABCDWXYZ', max_length=100)),
                ('timestamp', models.BigIntegerField(default=0)),
                ('trx_id', models.CharField(default='ABC123', max_length=40)),
            ],
        ),
    ]

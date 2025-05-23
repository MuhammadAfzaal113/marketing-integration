# Generated by Django 5.1.1 on 2025-04-28 18:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dblogs', '0001_initial'),
        ('webhook_integrate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='databaselogs',
            name='webhook',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webhook_integrate.webhook'),
        ),
        migrations.AlterField(
            model_name='databaselogs',
            name='error',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

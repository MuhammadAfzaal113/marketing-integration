# Generated by Django 5.1.1 on 2024-11-20 18:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webhook_integrate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='webhook',
            name='is_filter',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='User_info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=255, null=True)),
                ('webhook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webhook_integrate.webhook')),
            ],
        ),
    ]

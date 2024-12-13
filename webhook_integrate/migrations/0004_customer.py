# Generated by Django 5.1.1 on 2024-12-13 11:16

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webhook_integrate', '0003_filterkeys_delete_user_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('contact_id', models.CharField(max_length=255)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.CharField(max_length=255, unique=True)),
                ('phone', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]

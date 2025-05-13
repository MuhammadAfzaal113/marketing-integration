from django.db import models
from utils.abstract_models import CommonFields
from dblogs.enums import *
from webhook_integrate.models import Webhook
from datetime import timedelta
from django.utils.timezone import now

# Create your models here.

class DataBaseLogs(CommonFields):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    error = models.CharField(max_length=255, null=True, blank=True)
    webhook_version = models.CharField(max_length=50, choices=WEBHOOK_VERSION_CHOICES)
    level = models.CharField(max_length=50, choices=LEVEL_TYPE_CHOICES)
    action = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)

    def __str__(self):
        return f'{self.error}'
    
    def save(self, *args, **kwargs):
        two_weeks_ago = now() - timedelta(weeks=3)
        DataBaseLogs.objects.filter(created_at__lt=two_weeks_ago).delete()
        super().save(*args, **kwargs)
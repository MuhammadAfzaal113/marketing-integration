from django.db import models
from utils.abstract_models import CommonFields
from dblogs.enums import *

# Create your models here.

class DataBaseLogs(CommonFields):
    description = models.TextField()
    error = models.CharField(max_length=255)
    webhook_version = models.CharField(max_length=50, choices=WEBHOOK_VERSION_CHOICES)
    level = models.CharField(max_length=50, choices=LEVEL_TYPE_CHOICES)
    action = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)

    def __str__(self):
        return f'{self.error}'
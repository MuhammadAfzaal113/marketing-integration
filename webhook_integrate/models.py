from django.db import models
import uuid
from utils.abstract_models import CommonFields

class Shop(CommonFields):
    shop_name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)

    def __str__(self):
        return self.shop_name

class Webhook(CommonFields):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    webhook_name = models.CharField(max_length=255)
    webhook_url = models.CharField(max_length=255)
    is_filter = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.shop.shop_name} - {self.webhook_name}'

class Tag(CommonFields):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    tag_name = models.CharField(max_length=255)
    tag_id = models.CharField(max_length=255)

    def __str__(self):
        return self.tag_name


class CustomField(CommonFields):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    field_key = models.CharField(max_length=255)
    field_value = models.CharField(max_length=255)

    def __str__(self):
        return self.field_name


class ContactTag(CommonFields):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    tag_name = models.CharField(max_length=255)
    tag_value = models.CharField(max_length=255)

    def __str__(self):
        return self.tag_name


class FilterKeys(CommonFields):
    webhook = models.OneToOneField(Webhook, on_delete=models.CASCADE, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    total = models.CharField(max_length=255, null=True, blank=True)
    date = models.CharField(max_length=255, null=True, blank=True)
    

class Customer(CommonFields):
    customer_id = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.customer_id
    
class WebhookRequests(CommonFields):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    request_data = models.JSONField()

    def __str__(self):
        return f'{self.webhook.webhook_name}'
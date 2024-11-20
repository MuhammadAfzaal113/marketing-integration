from django.db import models
import uuid


class Shop(models.Model):
    shop_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    shop_name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)

    def __str__(self):
        return self.shop_name

class Webhook(models.Model):
    webhook_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    webhook_name = models.CharField(max_length=255)
    webhook_url = models.CharField(max_length=255)
    is_filter = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.shop.shop_name} - {self.webhook_name}'

class Tag(models.Model):
    tag_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    tag_name = models.CharField(max_length=255)
    tag_id = models.CharField(max_length=255)

    def __str__(self):
        return self.tag_name


class CustomField(models.Model):
    custom_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    field_id = models.CharField(max_length=255)

    def __str__(self):
        return self.field_name


class ContactTag(models.Model):
    contact_tag_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    tag_name = models.CharField(max_length=255)
    tag_id = models.CharField(max_length=255)

    def __str__(self):
        return self.tag_name


class FilterKeys(models.Model):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
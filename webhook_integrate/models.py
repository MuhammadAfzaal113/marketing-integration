from django.db import models
from utils.abstract_models import CommonFields
from webhook_integrate.choices import Operators

class Shop(models.Model):
    shop_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    shop_name = models.CharField(max_length=255)
    
    api_key = models.TextField(null=True, blank=True)
    tag_id = models.JSONField(null=True, blank=True)
    custom_fields = models.JSONField(null=True, blank=True)
    contact_tag = models.JSONField(null=True, blank=True)

    
    def __str__(self):
        return self.name
    
class Webhook(CommonFields):
    webhook_url = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def apply_filters(self, data):
        """
        Applies all filters associated with this webhook on the incoming data.
        """
        filters = self.filters.all()
        for webhook_filter in filters:
            if not webhook_filter.apply_filter(data):
                return False  # If any filter fails, stop processing
        return True  # All filters passed
    
class WebhookFilter(CommonFields):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    key = models.CharField(max_length=255, null=True, blank=True)
    value = models.CharField(max_length=255, null=True, blank=True)
    operator = models.CharField(max_length=50, choices=Operators.choices, null=True, blank=True)
    
    
    def __str__(self):
        return self.name
    
    def apply_filter(self, data):
        """
        Applies this filter to a data dictionary.
        """
        # Get the actual data value for the key
        actual_value = data.get(self.key)

        # Apply the condition based on the operator
        # if self.operator == Operators.EQUALS:
        #     return actual_value == self.value
        # elif self.operator == Operators.CONTAINS:
        #     return self.value in actual_value if isinstance(actual_value, str) else False
        # elif self.operator == Operators.GTE:
        #     return float(actual_value) >= float(self.value) if actual_value else False
        # elif self.operator == Operators.LTE:
        #     return float(actual_value) <= float(self.value) if actual_value else False
        # return False
    
class Customer(CommonFields):
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False, null=True, blank=True)
    is_invoice = models.BooleanField(default=False, null=True, blank=True)
    tags = models.JSONField( null=True, blank=True)
    source = models.CharField(max_length=255, default="AutoMojo API")
    customFields = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.name
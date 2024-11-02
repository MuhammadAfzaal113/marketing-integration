from django.db import models
from utils.abstract_models import CommonFields
from webhook_integrate.choices import Operators
from utils.helper import json_reader
from django.db.models import Q

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
    
    def apply_filters(self, data, is_and=None, is_or=None):
        """
        Applies all filters associated with this webhook on the incoming data.
        """
        query = Q()
        if is_and:
            query = Q(is_and=True)
            
        if is_or:
            query = Q(is_or=True)
            
        filters = WebhookFilter.objects.filter(query, webhook=self.id)
        for webhook_filter in filters:
            if not webhook_filter.apply_filter(data):
                return False  # If any filter fails, stop processing
        return True  # All filters passed
    
class WebhookFilter(CommonFields):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    
    key = models.CharField(max_length=255, null=True, blank=True)
    value = models.CharField(max_length=255, null=True, blank=True)
    operator = models.CharField(max_length=50, choices=Operators.choices, null=True, blank=True)
    is_and = models.BooleanField(default=False)
    is_or = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    def apply_filter(self, data):
        """
        Applies this filter to a data dictionary.
        """
        # Get the actual data value for the key
        actual_value = json_reader(data, self.key)
        
        if actual_value is None:
            return False # If the key does not exist in the data, return False
        
        # Apply the condition based on the operator
        if self.operator == Operators.DOSENOTCONTAINS:
            return self.value not in actual_value
        
        elif self.operator == Operators.CONTAINS:
            return self.value in actual_value
        
        elif self.operator == Operators.STARTWITH:
            return actual_value.startswith(self.value)
        
        elif self.operator == Operators.NOTSTARTWITH:
            return not actual_value.startswith(self.value)
        
        elif self.operator == Operators.ENDSWITH:
            return actual_value.endswith(self.value)
        
        elif self.operator == Operators.GREATER:
            return float(actual_value )> float(self.value)
        
        elif self.operator == Operators.LESS:
            return float(actual_value) < float(self.value)
        
        elif self.operator == Operators.AFTER:
            return actual_value > self.value
        
        elif self.operator == Operators.BEFORE:
            return actual_value < self.value
        
        elif self.operator == Operators.EQUALS:
            return actual_value == self.value
        
        elif self.operator == Operators.ISTRUE:
            return actual_value
        
        elif self.operator == Operators.ISFALSE:
            return not actual_value
        
        elif self.operator == Operators.DOESNOTEXIST:
            return actual_value is None
        
        elif self.operator == Operators.EXISTS:
            return actual_value is not None
        else:
            return False
    
class RequestData(CommonFields):
    data = models.JSONField(null=True, blank=True)
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
class WebhookAction(CommonFields):
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False, null=True, blank=True)
    is_invoice = models.BooleanField(default=False, null=True, blank=True)
    source = models.CharField(max_length=255, default="AutoMojo API")
    customFields = models.JSONField(null=True, blank=True)
    
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)    
    def __str__(self):
        return self.name
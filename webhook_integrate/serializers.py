from webhook_integrate.models import *
from rest_framework import serializers


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'shop_name', 'api_key']
        
class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'tag_name', 'tag_id']
        
class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = ['id', 'field_key', 'field_value']
        
        
class ContactTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactTag
        fields = ['id', 'tag_name', 'tag_value']
        
class Collect_DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterKeys
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'total', 'date']
        
class WebhookRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookRequests
        fields = ['request_data']
        
class WebhookSerializer(serializers.ModelSerializer):
    shop = serializers.StringRelatedField(source='shop.shop_name')
    webhook_filters = serializers.SerializerMethodField(read_only=True)
    custom_field = serializers.SerializerMethodField(read_only=True)
    contact_tag = serializers.SerializerMethodField(read_only=True)
    collect_data = serializers.SerializerMethodField(read_only=True)
    webhook_requests = serializers.SerializerMethodField(read_only=True)
    
    def get_WebhookRequests(self, obj):
        return WebhookRequestsSerializer(WebhookRequests.objects.filter(webhook=obj), many=True).data
    
    def get_webhook_filters(self, obj):
        return FilterSerializer(Tag.objects.filter(webhook_id=obj.id), many=True).data
    
    def get_custom_field(self, obj):
        print(obj.id)
        return CustomFieldSerializer(CustomField.objects.filter(webhook=obj), many=True).data

    def get_contact_tag(self, obj):
        return ContactTagSerializer(ContactTag.objects.filter(webhook=obj), many=True).data

    def get_collect_data(self, obj):
        return Collect_DataSerializer(FilterKeys.objects.filter(webhook=obj), many=True).data

    
    class Meta:
        model = Webhook
        fields = ['id', 'shop', 'webhook_name', 'webhook_url', 'is_filter', 'webhook_filters', 'custom_field', 'contact_tag', 'collect_data', 'webhook_requests']
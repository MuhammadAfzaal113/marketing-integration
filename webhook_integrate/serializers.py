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
        
class WebhookSerializer(serializers.ModelSerializer):
    shop = serializers.StringRelatedField(source='shop.shop_name')
    webhook_filters = serializers.SerializerMethodField(read_only=True)
    
    def get_filter(self, obj):
        return FilterSerializer(Tag.objects.filter(Webhook_id=obj.id), many=True).data
        
    class Meta:
        model = Webhook
        fields = ['id', 'shop', 'webhook_name', 'webhook_url', 'is_filter', 'webhook_filters']
from webhook_integrate.models import *
from rest_framework import serializers


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'shop_name', 'api_key']
        
class WebhookSerializer(serializers.ModelSerializer):
    shop = serializers.StringRelatedField(source='shop.shop_name')
    class Meta:
        model = Webhook
        fields = ['id', 'shop', 'webhook_name', 'webhook_url', 'is_filter']
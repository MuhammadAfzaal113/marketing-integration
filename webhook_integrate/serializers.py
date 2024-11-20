from webhook_integrate.models import Shop, Webhook, WebhookFilter, WebhookAction, RequestData
from rest_framework import serializers



class WebhookFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookFilter
        fields = ['id', 'key', 'value', 'operator', 'is_and', 'is_or']
        
class WebhookActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookAction
        fields = ['id','email', 'phone', 'first_name', 'last_name', 'creation_date', 'total_cost', 'is_paid', 'is_invoice', 'source', 'customFields']


class WebhookDetailsSerializer(serializers.ModelSerializer):
    filters = serializers.SerializerMethodField(read_only=True)
    actions = serializers.SerializerMethodField(read_only=True)
    
    def get_filters(self, obj):
        filters = WebhookFilter.objects.filter(webhook=obj)
        return WebhookFilterSerializer(filters, many=True).data
    
    def get_actions(self, obj):
        actions = WebhookAction.objects.filter(webhook=obj)
        return WebhookActionSerializer(actions, many=True).data
    
    class Meta:
        model = Webhook
        fields = ['id', 'webhook_url', 'filters', 'actions']
        

class RequestDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestData
        fields = ['id', 'data', 'created_at',]
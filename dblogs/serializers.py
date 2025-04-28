from rest_framework import serializers
from .models import DataBaseLogs

class DataBaseLogsSerializer(serializers.ModelSerializer):
    webhook = serializers.CharField(source='webhook.webhook_url', read_only=True)
    class Meta:
        model = DataBaseLogs
        fields = '__all__'

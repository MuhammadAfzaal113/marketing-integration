from rest_framework import serializers
from .models import DataBaseLogs

class DataBaseLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataBaseLogs
        fields = '__all__'

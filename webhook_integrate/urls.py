from django.urls import path, re_path
from .views import create_webhook, create_webhook_v2


urlpatterns = [
    path('admin/generate_webhook/', create_webhook, name='generate_webhook_url'),
    path('admin/generate_webhook_v2/', create_webhook_v2, name='generate_webhook_v2_url'),
]

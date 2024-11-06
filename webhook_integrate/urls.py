from django.urls import path, re_path
from .views import create_webhook


urlpatterns = [
    path('admin/generate_webhook/', create_webhook, name='generate_webhook_url'),
]

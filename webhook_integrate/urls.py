from django.urls import path
from .views import *


urlpatterns = [
    path('admin/generate_webhook/', create_webhook, name='generate_webhook_url'),
    path('admin/generate_webhook_v2/', create_webhook_v2, name='generate_webhook_v2_url'),
    
    #webhook_url
    path('generate-webhook-url-v1', generate_webhook_v1, name='generate_webhook_url'),
    path('generate-webhook-url-v2', generate_webhook_v2, name='generate_webhook_url_v2'),
    
    #shop 
    path('shop/create', create_shop, name='create_shop'),
    path('shop/update', update_shop, name='update_shop'),
    path('shop/delete', delete_shop, name='delete_shop'),
    path('get-shop-list', get_shop, name='get_shop_list'),
    
    #webhook
    path('webhook/create', create_webhook, name='create_webhook'),
    path('webhook/update', update_webhook, name='update_webhook'),
    path('webhook/delete', delete_webhook, name='delete_webhook'),
    path('get-webhook-list', get_webhook, name='get_webhook_list'),
]

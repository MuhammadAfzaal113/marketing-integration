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
    
    # filter
    path('filter/create', add_filter, name='create_filter'),
    path('filter/update', update_filter, name='update_filter'),
    path('filter/delete', delete_filter, name='delete_filter'),
    
    #custom field
    path('custom-field/create', add_custom_field, name='create_custom_field'),
    path('custom-field/update', update_custom_field, name='update_custom_field'),
    path('custom-field/delete', delete_custom_field, name='delete_custom_field'),
    
    #contact tag
    path('contact-tag/create', add_contact_tag, name='create_contact_tag'),
    path('contact-tag/update', update_contact_tag, name='update_contact_tag'),
    path('contact-tag/delete', delete_contact_tag, name='delete_contact_tag'),
    
    #collect data
    path('collect-data/create', add_collect_data, name='create_collect_data'),
    path('collect-data/update', update_collect_data, name='update_collect_data'),
    path('collect-data/delete', delete_collect_data, name='delete_collect_data'),
    
    #Generate Webhook URL
    path('generate-webhook-v1', generate_webhook_v1, name='generate_webhook_v1'),
    path('generate-webhook-v2', generate_webhook_v2, name='generate_webhook_v2'),
]

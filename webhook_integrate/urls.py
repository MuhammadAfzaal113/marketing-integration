
from django.urls import path
from webhook_integrate.views import *


urlpatterns = [
    path('generate-url', generate_url),
    path('get-webhook-list', get_webhook_list),
    path('create-filter', create_filter),
    path('get-webhook-list', get_webhook_list),
    path('create-action', create_action),
    path('update-action', update_action),
    path('update-filter', update_filter),
    path('delete-action', delete_action),
    path('delete-filter', delete_filter),
    path('get-webhook-details', get_webhook_details),
    path('get-request-data', get_request_data),
]


from django.urls import re_path, path
from webhook_integrate.views import *


urlpatterns = [
    path('generate-url', generate_url),
    path('get-webhook-list', get_webhook_list),
]

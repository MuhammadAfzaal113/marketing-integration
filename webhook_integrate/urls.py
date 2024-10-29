
from django.urls import re_path, path
from webhook_integrate.views import *


urlpatterns = [
    path('generate-url', generate_url),
]

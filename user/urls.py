from django.urls import re_path, path
from user.views import *

urlpatterns = [
    path('user/login', login_view),
]

"""
URL configuration for webhook project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings

from webhook_integrate.views import shopmonkey_webhook, shopmonkey_webhook_v2

urlpatterns = [
    re_path(r'^webhook/v2/(?P<webhook_url>[a-zA-Z0-9]+)', shopmonkey_webhook_v2),
    re_path(r'^webhook/(?P<webhook_url>[a-zA-Z0-9]+)', shopmonkey_webhook),
    path('hook/api/v1/', include('webhook_integrate.urls')),
    path('hook/api/v1/', include('user.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

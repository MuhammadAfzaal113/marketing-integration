from django.urls import path
from .views import *


urlpatterns = [
    path('logs/get-logs-list', get_database_logs, name='get-database-logs'),
    path('logs/delete', delete_database_log, name='delete-database-log'),
]

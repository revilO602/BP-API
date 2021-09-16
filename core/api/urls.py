from django.urls import path
from core.api.views import uptime

app_name = 'blog'

urlpatterns = [
    path('uptime/', uptime, name="uptime"),
]

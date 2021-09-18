from django.urls import path
from core.api.views import uptime

app_name = 'core'

urlpatterns = [
    path('uptime/', uptime, name="uptime"),
]

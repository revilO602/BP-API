from django.urls import path
from core.api.views import uptime, DeliveryStateView
from core.api.views import (
        CreateDeliveryView,
        RetrieveDeliveryView,
        ListDeliveryView
    )
app_name = 'core'

urlpatterns = [
    path('uptime/', uptime, name="uptime"),
    path('create_delivery/', CreateDeliveryView.as_view(), name="create_delivery"),
    path('get_delivery/', RetrieveDeliveryView.as_view(), name="retrieve_delivery"),
    path('my_deliveries/', ListDeliveryView.as_view(), name="list_deliveries"),
    path('deliveries/<safe_id>/state', DeliveryStateView.as_view(), name="delivery_state"),
]

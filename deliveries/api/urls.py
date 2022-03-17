from django.urls import path
from deliveries.api.views import uptime, DeliveryStateView
from deliveries.api.views import DeliveriesView, DeliveryDetailView
app_name = 'deliveries'

urlpatterns = [
    path('uptime/', uptime, name="uptime"),
    path('', DeliveriesView.as_view(), name="deliveries"),
    path('<str:delivery_id>', DeliveryDetailView.as_view(), name="delivery_detail"),
    path('<str:safe_delivery_id>/state', DeliveryStateView.as_view(), name="delivery_state"),
]

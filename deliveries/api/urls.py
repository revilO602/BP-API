from django.urls import path
from deliveries.api.views import uptime, DeliveryStateView, DeliveriesStatisticsView, \
    DeliveriesView, DeliveryDetailView, DeliveriesPreviewView

app_name = 'deliveries'

urlpatterns = [
    path('uptime/', uptime, name="uptime"),
    path('', DeliveriesView.as_view(), name="deliveries"),
    path('statistics', DeliveriesStatisticsView.as_view(), name="deliveries_statistics"),
    path('preview', DeliveriesPreviewView.as_view(), name="deliveries_preview"),
    path('<str:delivery_id>', DeliveryDetailView.as_view(), name="delivery_detail"),
    path('<str:safe_delivery_id>/state', DeliveryStateView.as_view(), name="delivery_state"),
]

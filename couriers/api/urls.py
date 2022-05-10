from django.urls import path

from couriers.api.views import (
    CouriersView, ListClosestDeliveryView,
)

app_name = 'accounts'

urlpatterns = [
    path('closest_deliveries/', ListClosestDeliveryView.as_view(), name="closest_deliveries"),
    path('', CouriersView.as_view(), name="couriers"),
]

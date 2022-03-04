from django.urls import path

from couriers.api.views import (
    CreateCourierView, AcceptDeliveryView, ListClosestDeliveryView,
)

app_name = 'account'

urlpatterns = [
    path('become_courier/', CreateCourierView.as_view(), name="become_courier"),
    path('accept_delivery/', AcceptDeliveryView.as_view(), name="accept_delivery"),
    path('closest_deliveries/', ListClosestDeliveryView.as_view(), name="closest_deliveries")
]

# routing config for websockets and ASGI
from django.urls import path

from couriers.websockets import consumers

websocket_urlpatterns = [
    path('ws/couriers/<delivery_id>/', consumers.CourierConsumer.as_asgi()),
    path('ws/couriers/', consumers.CourierConsumer.as_asgi())
]
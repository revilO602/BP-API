from django.urls import path

from routes.api.views import RouteViewSet

app_name = 'routes'

urlpatterns = [
    path('<str:pk>/', RouteViewSet.as_view({'get': 'retrieve'}), name="routes_detail"),
    path('', RouteViewSet.as_view({'get': 'list'}), name="routes"),
]

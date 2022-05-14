from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from url_filter.integrations.drf import DjangoFilterBackend

from routes.api.serializers import RouteSerializer
from routes.models import Route


class RouteViewSet(viewsets.ModelViewSet):
    """
    Viewset to retrieve and list routes of deliveries.
    * Allows filtering and searching based on pickup and delivery addresses
    """
    queryset = Route.objects.all().order_by('-created_at')
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['delivery']
    pagination_class = LimitOffsetPagination

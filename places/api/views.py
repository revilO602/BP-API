from rest_framework import viewsets
from url_filter.integrations.drf import DjangoFilterBackend

from places.api.serializers import RouteSerializer
from places.models import Route


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['username', 'email']




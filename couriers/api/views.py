from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Q
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from couriers.permissions import IsCourier
from deliveries.api.google_api import get_distance_for_sort
from deliveries.api.serializers import SafeDeliverySerializer
from deliveries.models import Delivery
from couriers.api.serializers import CourierSerializer
from helpers.enums import SizeType


class CouriersView(APIView):
    """
    View that handles operations on couriers
    * Requires authentication by a JWT token. Returns a 401 response if user is not authenticated.
    """
    serializer_class = CourierSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Register authenticated user as a courier.

        :param request: HTTP POST request with courier data in body.
        :return: HTTP Response - 201 if success, 400 if invalid body or user already is a courier
        """
        user = request.user
        if user.courier:
            return Response({'error': "User already registered as courier"}, status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        courier = serializer.save()
        user.courier = courier
        user.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class ListClosestDeliveryView(GenericAPIView):
    """
    View to retrieve closest deliveries.
    """
    serializer_class = SafeDeliverySerializer
    permission_classes = [IsAuthenticated, IsCourier]

    def get_queryset(self):
        """
        Get query set of 'ready' deliveries
        :return: query set of deliveries in the 'ready' state
        """
        qs = Delivery.objects.filter(state='ready')
        return qs

    def get_route_distance(self, delivery):
        """
        Get route distance from courier to delivery pick up place

        :param delivery: delivery object
        :return: route distance for driving between coordinates and pick up place of delivery - positive integer in meters
        """
        return get_distance_for_sort(delivery, self.latitude, self.longitude)

    def sort_based_on_route_distance(self, deliveries):
        """
        Sort deliveries based on their route distance
        :param deliveries: the deliveries query set
        :return: sorted array of deliveries based on route distance
        """
        return sorted(deliveries, key=self.get_route_distance)

    def get(self, request):
        """
        List 10 ready deliveries ordered by closest to coordinates given as query params.
        Size of delivery must be equal or smaller that size of courier vehicle to be retrieved.

        :param request: HTTP GET request with query params:
                        longitude and latitude of courier - example: /?lon=52,25486&lat=24,6589 .
        :return: list of delivery objects with safe info of the delivery
        """
        vehicle_type = request.user.courier.vehicle_type
        qs = self.get_queryset()
        if vehicle_type == SizeType.SMALL:
            qs = qs.filter(Q(item__size=SizeType.SMALL))
        elif vehicle_type == SizeType.MEDIUM:
            qs = qs.filter(Q(item__size=SizeType.SMALL) | Q(item__size=SizeType.MEDIUM))
        self.longitude = self.request.query_params.get('lon', '0,0')
        self.latitude = self.request.query_params.get('lat', '0,0')
        self.longitude = float(self.longitude.replace(',', '.'))
        self.latitude = float(self.latitude.replace(',', '.'))
        courier_location = Point(self.longitude, self.latitude, srid=4326)
        qs = qs.select_related('pickup_place').annotate(
            distance=Distance('pickup_place__coordinates', courier_location)
        ).order_by('distance')[:10]
        serializer = self.get_serializer(qs, many=True)
        closest_deliveries = self.sort_based_on_route_distance(serializer.data)
        return Response(closest_deliveries)


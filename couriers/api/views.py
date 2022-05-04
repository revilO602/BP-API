from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from deliveries.api.serializers import SafeDeliverySerializer
from deliveries.models import Delivery
from couriers.api.serializers import CourierSerializer


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
    View to list 10 ready deliveries ordered by closest to coordinates given as query params.
    Size of delivery must be equal or smaller that size of courier vehicle to be retrieved.
    * Return list of deliveries with safe info of the delivery.
    * Query params: longitude and latitude of courier - example: /?lon=52,25486&lat=24,6589 .
    """
    serializer_class = SafeDeliverySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Delivery.objects.filter(state='ready')
        longitude = self.request.query_params.get('lon', None)
        latitude = self.request.query_params.get('lat', None)
        if longitude is not None and latitude is not None:
            longitude = float(longitude.replace(',', '.'))
            latitude = float(latitude.replace(',', '.'))
            courier_location = Point(longitude, latitude, srid=4326)
            qs = qs.select_related('pickup_place').annotate(
                distance=Distance('pickup_place__coordinates', courier_location)
            ).order_by('distance')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


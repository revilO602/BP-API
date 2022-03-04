from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView

from core.api.serializers import ClientDeliverySerializer, SafeDeliverySerializer
from core.models import Delivery
from couriers.api.serializers import CourierSerializer
from couriers.models import Courier


class CreateCourierView(APIView):
    """
    View to add courier information to user. Authenticated user automatically gets the
    courier information added to account.

    * Return info of the created courier.
    """
    serializer_class = CourierSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = CourierSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        try:
            courier = serializer.save()
            courier.user = request.user
            courier.person = request.user.person
            courier.save()
        except IntegrityError:
            return Response({'error': "User already registered as courier"}, status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status.HTTP_201_CREATED)

@extend_schema(
    parameters=[OpenApiParameter(
        name='lon',
        type=str,
        location=OpenApiParameter.QUERY,
        required=True,
        style='form',
        description='Longitude of courier with comma: e.g. lon=25,658',
    ), OpenApiParameter(
        name='lat',
        type=str,
        location=OpenApiParameter.QUERY,
        required=True,
        style='form',
        description='Latitude of courier with comma: e.g. lat=25,658',
    )],
)
class ListClosestDeliveryView(GenericAPIView):
    """
    View to list ready deliveries ordered by closest to coordinates given as query params.

    * Return list of deliveries with safe info of the delivery.
    * Query params: /?lon=52,25486&lat=24,6589 .
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
        # result_page = paginator.paginate_queryset(delivery, request)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class AcceptDeliveryView(APIView):
    """
    View for courier to accept a delivery request. Assigns the delivery to the authenticated courier.
    Use the safe_id of the delivery as a query parameter. Delivery can only be accepted if its in the 'ready' state.

    * Returns all information about the accepted delivery.
    """
    serializer_class = ClientDeliverySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        id = request.query_params.get('id')
        try:
            delivery = Delivery.objects.get(safe_id=id)
        except Delivery.DoesNotExist:
            return Response({None}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        if delivery.state != 'ready':
            return Response({"error": 'Delivery is not ready to be assigned'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            courier = Courier.objects.get(user=request.user)
        except Courier.DoesNotExist:
            return Response({"error": "You are not a registered courier"}, status=status.HTTP_401_UNAUTHORIZED)
        delivery.courier = courier
        delivery.state = 'assigned'
        delivery.save()
        serializer = ClientDeliverySerializer(delivery)
        return Response(serializer.data)

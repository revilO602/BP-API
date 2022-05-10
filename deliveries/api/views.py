import googlemaps.exceptions
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import connection
from django.http import JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from deliveries.api.emails import delivery_start_receiver_email
from deliveries.api.google_api import get_distance, get_route
from deliveries.api.serializers import DeliverySerializer, SafeDeliverySerializer
from deliveries.models import Delivery
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db.models import Case, Value, When
import json
from deliveries.permissions import CanChangeDeliveryState
from helpers.functions import is_state_change_valid, calculate_price
from django.db.models.functions import TruncMonth
from django.db.models import Count
import datetime
from dateutil.relativedelta import relativedelta
from routes.api.serializers import RouteSerializer


def create_route(delivery):
    """
    Create a route entry for delivery.

    :param delivery: Delivery object
    """
    steps, polyline = get_route(delivery.pickup_place.place_id, delivery.delivery_place.place_id)
    data = {
        'steps': steps,
        'polyline': polyline
    }
    serializer = RouteSerializer(data=data)
    if not serializer.is_valid(raise_exception=True):
        print("a problem")
        return
    route = serializer.save()
    route.delivery = delivery
    route.save()

@api_view(['GET', ])
def uptime(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime;")
        row = cursor.fetchone()
    uptime = str(row[0])
    uptime = uptime.replace(',', '')
    return JsonResponse({"psql": {"uptime": uptime}})


class DeliveriesView(GenericAPIView):
    """
    View that handles operations on deliveries.
    """
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """
        Get a queryset of deliveries from users history.
        * Deliveries are annotated by users role in them - sender/receiver/courier

        :return: Query set with 100 deliveries
        """
        user = self.request.user
        courier = self.request.query_params.get('courier')
        if courier:
            deliveries = Delivery.objects.filter(courier=user)
            deliveries = deliveries.annotate(user_is=Value('courier'))
        else:
            deliveries = Delivery.objects.filter(Q(sender=user.person) | Q(receiver_account=user))
            deliveries = deliveries.annotate(user_is=Case(
                When(sender=user.person, then=Value('sender')),
                When(receiver_account=user, then=Value('receiver')),
                default=Value('unknown'), ))
        return deliveries[:100]

    def post(self, request):
        """
        Create a new delivery, it starts in the 'ready' state.

        :param request: HTTP POST request with form data of a new delivery in body.
        :return: HTTP Response - 200 with delivery data if success, 400 if invalid body
        """
        serializer = self.get_serializer(data=request.data, context={'sender': request.user.person})
        # if not serializer.is_valid(raise_exception=True):
        #     return Response(serializer.errors, status=400)
        serializer.is_valid(raise_exception=True)
        try:
            distance, duration = get_distance(serializer.validated_data["pickup_place"]["place_id"],
                                              serializer.validated_data["delivery_place"]["place_id"])

        except googlemaps.exceptions.HTTPError:
            return Response({"error": "Invalid place Id"})
        delivery = serializer.create(serializer.validated_data)
        delivery.route_distance = distance["value"]
        delivery.expected_duration = duration["value"]
        delivery.price = calculate_price(distance["value"], delivery.item.size, delivery.item.weight)
        delivery.save()
        delivery_start_receiver_email(delivery)
        create_route(delivery)
        return Response(self.get_serializer(instance=delivery).data, status.HTTP_201_CREATED)

    def get(self, request):
        """
        Retrieve a list of deliveries from the users history.

        :param request: HTTP GET request with delivery ID in URL.
        :return: HTTP Response - 200 with deliveries data if success, 404 if not found
        """
        deliveries = self.get_queryset()
        serializer = self.get_serializer(deliveries, many=True)
        return Response(serializer.data)


class DeliveryDetailView(APIView):
    """
    View that handles operations on one delivery.
    """
    serializer_class = DeliverySerializer

    def get_object(self, delivery_id, user):
        delivery = Delivery.objects.filter(id=delivery_id)
        if not delivery:
            raise Http404
        delivery = delivery.annotate(user_is=Case(
            When(sender=user.person, then=Value('sender')),
            When(receiver_account=user, then=Value('receiver')),
            When(courier=user, then=Value('courier')),
            default=Value('unknown'), ))
        return delivery.first()

    def get(self, request, delivery_id):
        """
        Retrieve one delivery by its ID
        * Deliveries are annotated by users role in them - sender/receiver/courier

        :return: Delivery object
        """
        try:
            delivery = self.get_object(delivery_id, request.user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(delivery)
        return Response(serializer.data)


class DeliveryStateView(APIView):
    """
    View for courier to change state of delivery - includes accepting a delivery
    """
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated, CanChangeDeliveryState]

    def get_object(self, safe_delivery_id):
        """
        Retrieve delivery by its safe ID - this ID allows only non-sensitive data to be viewed.

        :param safe_delivery_id: safe_id of the delivery.
        :return: Delivery object.
        """
        delivery = Delivery.objects.filter(safe_id=safe_delivery_id)
        delivery = delivery.annotate(user_is=Value('courier')).first()
        if not delivery:
            raise Http404
        self.check_object_permissions(self.request, delivery)
        return delivery

    def patch(self, request, safe_delivery_id):
        """
        Updates the state of the delivery.

        :param request: HTTP Patch request containing the new state of delivery in body.
        :param safe_delivery_id: safe ID of the delivery.
        :return: HTTP response - 200 with delivery data including sensitive data (since courier
                 is now assigned to the delivery) if success, 400 if invalid body, 404 if not found
        """
        try:
            delivery = self.get_object(safe_delivery_id)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_state = json.loads(request.body)['state']
        except KeyError:
            return Response({'error': 'State not included, please use {"state": "new_state"}'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not is_state_change_valid(delivery.state, new_state):
            return Response({"error": "Invalid state change"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if new_state == 'assigned':
            delivery.courier = request.user
        if new_state == 'delivered':
            delivery_start_receiver_email(delivery)
        delivery.state = new_state
        delivery.save()
        serializer = self.serializer_class(delivery)
        return Response(serializer.data)


class DeliveriesStatisticsView(GenericAPIView):
    """
    View to retrieve statistics of deliveries for user.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve monthly statistics of sent deliveries.

        :return: query set annotated with the number of deliveries a user sent per month
        """
        today = datetime.date.today()
        user = self.request.user
        months = self.request.query_params.get('months')
        if not months:
            months = 5
        start = today - relativedelta(months=months)
        today += datetime.timedelta(days=1)
        stats = Delivery.objects.filter(sender=user.person, created_at__range=[start, today]) \
            .annotate(month=TruncMonth('created_at')) \
            .values('month') \
            .annotate(count=Count('id')) \
            .values('month', 'count')
        return stats

    def get(self, request):
        """
        Retrieve number of sent deliveries for user per month.

        :param request: HTTP GET request with the amount of months as query param.
        :return: HTTP Response - 200 with requested data
        """
        stats = self.get_queryset()
        return Response(stats)


class DeliveriesPreviewView(GenericAPIView):
    """
    View that allows to retrieve a preview of the delivery before creating it.
    """
    serializer_class = SafeDeliverySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Retrieve a preview of the distance, duration and price of a delivery.

        :param request: HTTP POST request with the data of the delivery in body.
        :return: HTTP Response - 200 with duration. distance and price of successful, 400 if invalid body
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        size = serializer.validated_data["size"] if "size" in serializer.validated_data else "medium"
        weight = serializer.validated_data["weight"] if "weight" in serializer.validated_data else "medium"
        try:
            print(serializer.validated_data["pickup_place"]["place_id"],
                  serializer.validated_data["delivery_place"]["place_id"])
            distance, duration = get_distance(serializer.validated_data["pickup_place"]["place_id"],
                                              serializer.validated_data["delivery_place"]["place_id"])
            price = calculate_price(distance["value"], size, weight)
            return Response({"distance": distance, "duration": duration, "price": price})
        except googlemaps.exceptions.HTTPError:
            return Response({"error": "Invalid place Id"})

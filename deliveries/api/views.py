from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import connection
from django.http import JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from deliveries.api.serializers import DeliverySerializer, SafeDeliverySerializer
from deliveries.models import Delivery
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db.models import Case, Value, When
# from pagination import PageSizePagination
import json
from deliveries.permissions import CanChangeDeliveryState
from couriers.models import Courier
from helpers.functions import is_state_change_valid


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
    View to create a delivery. Authenticated user automatically becomes the sender of the delivery.

    * Return info of the created delivery.
    """
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'sender': request.user.person})
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        delivery = serializer.create(serializer.validated_data)
        return Response(self.get_serializer(instance=delivery).data, status.HTTP_201_CREATED)

    def get(self, request):
        # paginator = self.pagination_class()
        user = request.user
        delivery = Delivery.objects.filter(Q(sender=user.person) | Q(receiver_account=user))
        delivery = delivery.annotate(user_is=Case(
            When(sender=user.person, then=Value('sender')),
            When(receiver_account=user, then=Value('receiver')),
            default=Value('unknown'), ))
        # result_page = paginator.paginate_queryset(delivery, request)
        serializer = self.get_serializer(delivery, many=True)
        return Response(serializer.data)


class DeliveryDetailView(APIView):
    """
    View to get information of delivery by ID.

    * Return info of the created delivery.
    """
    serializer_class = DeliverySerializer

    def get_object(self, delivery_id):
        return get_object_or_404(Delivery, id=delivery_id)

    def get(self, request, delivery_id):
        try:
            delivery = self.get_object(delivery_id)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(delivery)
        return Response(serializer.data)


class DeliveryStateView(APIView):
    """
    View for courier to change state of delivery - includes accepting a delivery:
     Assigns the delivery to the authenticated courier. Delivery can only be accepted if its in the 'ready' state.
    Use the safe_id of the delivery as a query parameter.

    * Returns all information about the accepted delivery.
    """
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated, CanChangeDeliveryState]

    def get_object(self, safe_delivery_id):
        try:
            obj = Delivery.objects.get(safe_id=safe_delivery_id)
            self.check_object_permissions(self.request, obj)
            return obj
        except Delivery.DoesNotExist:
            raise Http404

    def patch(self, request, safe_delivery_id):
        try:
            delivery = self.get_object(safe_delivery_id)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_state = json.loads(request.body)['state']
        except KeyError:
            return Response({'error': 'State not included, please use {"state": "new_state"}'}, status=status.HTTP_400_BAD_REQUEST)
        if not is_state_change_valid(delivery.state, new_state):
            return Response({"error": "Invalid state change"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if new_state == 'assigned':
            delivery.courier = request.user
        delivery.state = new_state
        delivery.save()
        serializer = self.serializer_class(delivery)
        return Response(serializer.data)

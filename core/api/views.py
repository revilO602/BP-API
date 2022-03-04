from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from core.api.serializers import CreateDeliverySerializer, ClientDeliverySerializer, SafeDeliverySerializer
from core.models import Delivery
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db.models import Case, Value, When
# from pagination import PageSizePagination
import json
from core.permissions import CanChangeDeliveryState
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


@extend_schema(
    parameters=[OpenApiParameter(
        name='coordinates',
        type=str,
        location=OpenApiParameter.QUERY,
        required=True,
        style='form',
        description='Properly formatted WKT(EWKT) coordinates. ! LONGITUDE FIRST, LATITUDE SECOND !',
        examples=[
            OpenApiExample(
                'Example',
                value='"POINT(17.10818515071519 48.097275508021475)"'
            ),
        ],
    ), OpenApiParameter(
        name='photo',
        type=str,
        location=OpenApiParameter.QUERY,
        required=False,
        style='form',
        description='Nested image file of the item', )])
class CreateDeliveryView(APIView):
    """
    View to create a delivery. Authenticated user automatically becomes the sender of the delivery.

    * Return info of the created delivery.
    """
    serializer_class = CreateDeliverySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'sender': request.user.person})
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


@extend_schema(
    parameters=[OpenApiParameter(
        name='id',
        type=str,
        location=OpenApiParameter.QUERY,
        required=True,
        style='form',
        description='Return delivery with given ID',
    )],
)
class RetrieveDeliveryView(GenericAPIView):
    """
    View to get information of delivery by ID.

    * Return info of the created delivery.
    """
    serializer_class = CreateDeliverySerializer

    def get(self, request):
        id = request.query_params.get('id')
        try:
            delivery = Delivery.objects.get(id=id)
        except Delivery.DoesNotExist:
            return Response({None}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(delivery)
        return Response(serializer.data)


class ListDeliveryView(GenericAPIView):
    """
    View to list deliveries of authenticated user - sender or receiver.

    * Return info of the created delivery.
    """
    serializer_class = CreateDeliverySerializer
    permission_classes = [IsAuthenticated]

    # pagination_class = PageSizePagination

    def get(self, request):
        # paginator = self.pagination_class()
        user = request.user.person
        delivery = Delivery.objects.filter(Q(sender=user) | Q(receiver=user))
        delivery = delivery.annotate(user_is=Case(
            When(sender=user, then=Value('sender')),
            When(receiver=user, then=Value('receiver')),
            default=Value('unknown'), ))
        # result_page = paginator.paginate_queryset(delivery, request)
        serializer = self.get_serializer(delivery, many=True)
        return Response(serializer.data)


class DeliveryStateView(APIView):
    """
    View for courier to change state of delivery - includes accepting a delivery:
     Assigns the delivery to the authenticated courier. Delivery can only be accepted if its in the 'ready' state.
    Use the safe_id of the delivery as a query parameter.

    * Returns all information about the accepted delivery.
    """
    serializer_class = CreateDeliverySerializer
    permission_classes = [IsAuthenticated, CanChangeDeliveryState]

    def patch(self, request, safe_id):
        try:
            delivery = Delivery.objects.get(safe_id=safe_id)
        except Delivery.DoesNotExist:
            return Response({None}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_state = json.loads(request.body)['state']
        except KeyError:
            return Response({'error': 'State not included, please use {"state": "new_state"}'}, status=status.HTTP_400_BAD_REQUEST)
        if not is_state_change_valid(delivery.state, new_state):
            return Response({"error": "Invalid state change"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if new_state == 'ready':
            delivery.courier = Courier.objects.get(user=request.user)
        delivery.state = new_state
        delivery.save()
        serializer = self.serializer_class(delivery)
        return Response(serializer.data)

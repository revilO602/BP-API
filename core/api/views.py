from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from core.api.serializers import CreateDeliverySerializer, ClientDeliverySerializer
from core.models import Delivery
from django.db.models import Q
from django.db import transaction

# Respond with json of uptime



@api_view(['GET', ])
def uptime(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime;")
        row = cursor.fetchone()
    uptime = str(row[0])
    uptime = uptime.replace(',', '')
    return JsonResponse({"psql": {"uptime": uptime}})


class CreateDeliveryView(APIView):
    """
    View to create a delivery. Authenticated user automatically becomes the sender of the delivery.

    * Return info of the created delivery.
    """
    serializer_class = CreateDeliverySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request):
        print(request.data)
        serializer = CreateDeliverySerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.data)
            return Response(serializer.errors, status=400)
        delivery = serializer.save(sender=request.user.person)
        data = {'id': delivery.id, 'data': serializer.data}
        return Response(data, status.HTTP_201_CREATED)


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
    View to get information of delivery by authenticated user - sender or receiver.

    * Return info of the created delivery.
    """
    serializer_class = ClientDeliverySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user.person
        id = request.query_params.get('id')
        delivery = Delivery.objects.get(id=id)
        if delivery.sender == user or delivery.receiver == user:
            serializer = self.get_serializer(delivery)
            return Response(serializer.data)
        else:
            return Response({'error': "You don't have access to this"}, status.HTTP_401_UNAUTHORIZED)


class ListDeliveryView(GenericAPIView):
    """
    View to list deliveries of authenticated user - sender or receiver.

    * Return info of the created delivery.
    """
    serializer_class = ClientDeliverySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user.person
        delivery = Delivery.objects.filter(Q(sender=user) | Q(receiver=user))
        serializer = self.get_serializer(delivery, many=True)
        return Response(serializer.data)



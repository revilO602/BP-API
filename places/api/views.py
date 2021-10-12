from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import connection
from django.http import JsonResponse
from core.api.serializers import CreateDeliverySerializer, ClientDeliverySerializer
from core.models import Delivery
from django.db.models import Q




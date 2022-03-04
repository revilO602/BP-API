from rest_framework import serializers

from account.api.serializers import PersonSerializer
from couriers.models import Courier


class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = ['id', 'id_photo_front', 'id_photo_back', 'dl_photo_front',
                  'dl_photo_back', 'vehicle_type', 'home_address', 'coordinates']


class CourierSerializerForDelivery(serializers.ModelSerializer):
    person = PersonSerializer()

    class Meta:
        model = Courier
        fields = ['vehicle_type', 'coordinates', 'person']

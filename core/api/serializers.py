from rest_framework import serializers
from core.models import Item, Delivery
from account.api.serializers import PersonSerializer
from places.api.serializers import PlaceSerializer
from drf_writable_nested.serializers import WritableNestedModelSerializer


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'description', 'photo', 'size', 'weight', 'fragile']


class CreateDeliverySerializer(WritableNestedModelSerializer):
    receiver = PersonSerializer()
    item = ItemSerializer()
    pickup_place = PlaceSerializer()
    delivery_place = PlaceSerializer()

    class Meta:
        model = Delivery
        fields = ['id', 'item', 'receiver', 'pickup_place', 'delivery_place']


class ClientDeliverySerializer(WritableNestedModelSerializer):
    receiver = PersonSerializer()
    sender = PersonSerializer()
    item = ItemSerializer()
    pickup_place = PlaceSerializer()
    delivery_place = PlaceSerializer()

    class Meta:
        model = Delivery
        fields = ['id', 'item', 'sender', 'receiver', 'pickup_place', 'delivery_place']



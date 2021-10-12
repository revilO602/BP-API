from rest_framework import serializers
from core.models import Item, Delivery
from account.api.serializers import PersonSerializer
from drf_writable_nested.serializers import WritableNestedModelSerializer

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'description', 'photo']


class CreateDeliverySerializer(WritableNestedModelSerializer):
    receiver = PersonSerializer()
    item = ItemSerializer()

    class Meta:
        model = Delivery
        fields = ['item', 'receiver']


class ClientDeliverySerializer(WritableNestedModelSerializer):
    receiver = PersonSerializer()
    sender = PersonSerializer()
    item = ItemSerializer()

    class Meta:
        model = Delivery
        fields = ['item', 'sender', 'receiver']



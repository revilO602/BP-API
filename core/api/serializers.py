from django.http import QueryDict
from rest_framework import serializers

from account.models import Person
from core.models import Item, Delivery
from places.models import Place
from account.api.serializers import PersonSerializer
from places.api.serializers import PlaceSerializer
from couriers.api.serializers import CourierSerializer, CourierSerializerForDelivery
from drf_writable_nested.serializers import WritableNestedModelSerializer


def get_existing_person(data):
    try:
        return Person.objects.get(email=data['email'], first_name=data['first_name'],
                                  last_name=data['last_name'], phone_number=data['phone_number'])
    except Person.DoesNotExist:
        return None


def get_existing_place(data):
    given_id = data['place_id']
    try:
        return Place.objects.get(place_id=given_id)
    except Place.DoesNotExist:
        return None


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'description', 'photo', 'size', 'weight', 'fragile']


class CreateDeliverySerializer(WritableNestedModelSerializer):
    receiver = PersonSerializer()
    item = ItemSerializer()
    pickup_place = PlaceSerializer()
    delivery_place = PlaceSerializer()
    user_is = serializers.StringRelatedField(allow_null=True, allow_empty=True, required=False)
    courier = CourierSerializerForDelivery(allow_null=True, required=False)

    class Meta:
        model = Delivery
        fields = ['id', 'created_at', 'user_is', 'item', 'sender', 'receiver', 'pickup_place', 'delivery_place',
                  'courier', 'state']

    def create(self, validated_data):
        sender = self.context['sender']
        pickup_place = Place.objects.get_or_create(place_id=validated_data['pickup_place']['place_id'])[0]
        delivery_place = Place.objects.get_or_create(place_id=validated_data['delivery_place']['place_id'])[0]
        receiver = Person.objects.get_or_create(**validated_data.pop('receiver'))[0]
        item = Item.objects.create(**validated_data.pop('item'))
        delivery = Delivery.objects.create(
            item=item,
            sender=sender,
            receiver=receiver,
            pickup_place=pickup_place,
            delivery_place=delivery_place
        )
        return delivery

    def update(self, instance, validated_data):
        instance.state = validated_data.get('state', instance.state)
        instance.save()
        return instance


class ClientDeliverySerializer(WritableNestedModelSerializer):
    receiver = PersonSerializer()
    sender = PersonSerializer()
    item = ItemSerializer()
    pickup_place = PlaceSerializer()
    delivery_place = PlaceSerializer()
    user_is = serializers.StringRelatedField(allow_null=True, allow_empty=True, required=False)
    courier = CourierSerializerForDelivery(allow_null=True, required=False)

    class Meta:
        model = Delivery
        fields = ['id', 'created_at', 'user_is', 'item', 'sender', 'receiver', 'pickup_place', 'delivery_place',
                  'courier', 'state']



class SafeDeliverySerializer(WritableNestedModelSerializer):
    item = ItemSerializer()
    pickup_place = PlaceSerializer()
    delivery_place = PlaceSerializer()

    class Meta:
        model = Delivery
        fields = ['safe_id', 'created_at', 'item', 'pickup_place', 'delivery_place', 'state']


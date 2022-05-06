from django.contrib.gis.geos import Point
from rest_framework import serializers
from accounts.models import Person, Account
from deliveries.models import Item, Delivery
from places.models import Place
from accounts.api.serializers import PersonSerializer, AccountSerializer
from places.api.serializers import PlaceSerializer


class ItemSerializer(serializers.ModelSerializer):
    """ Serializer for item instances """
    class Meta:
        model = Item
        fields = ['name', 'description', 'photo', 'size', 'weight', 'fragile']


class DeliverySerializer(serializers.ModelSerializer):
    """ Serializer for delivery instances """
    receiver = PersonSerializer()
    sender = PersonSerializer(read_only=True)
    item = ItemSerializer()
    pickup_place = PlaceSerializer()
    delivery_place = PlaceSerializer()
    user_is = serializers.StringRelatedField(allow_null=True, allow_empty=True, required=False)
    courier = AccountSerializer(allow_null=True, required=False)

    class Meta:
        model = Delivery
        fields = ['id', 'created_at', 'user_is', 'item', 'sender', 'receiver', 'pickup_place', 'delivery_place',
                  'courier', 'state', 'expected_duration', 'route_distance', 'price']
        read_only_fields = ['id', 'created_at', 'state', 'expected_duration', 'route_distance', 'price']

    def create(self, validated_data):
        """
        Create a new delivery - first state is always 'ready'

        :param validated_data: data of the serializer after validation
        :return: created delivery instance
        """
        pickup_place_data = validated_data.pop('pickup_place')
        delivery_place_data = validated_data.pop('delivery_place')
        receiver_data = validated_data.pop('receiver')
        item_data = validated_data.pop('item')
        pickup_place_coordinates = Point(pickup_place_data.pop('longitude'), pickup_place_data.pop('latitude'))
        delivery_place_coordinates = Point(delivery_place_data.pop('longitude'), delivery_place_data.pop('latitude'))
        delivery = Delivery.objects.create(
            item=Item.objects.create(**item_data),
            sender=self.context['sender'],
            receiver=Person.objects.get_or_create(**receiver_data)[0],
            receiver_account=Account.objects.filter(email=receiver_data['email']).first(),
            pickup_place=Place.objects.get_or_create(**pickup_place_data,
                                                   defaults={'coordinates': pickup_place_coordinates})[0],
            delivery_place=Place.objects.get_or_create(**delivery_place_data,
                                                       defaults={'coordinates': delivery_place_coordinates})[0],
        )
        return delivery


class SafeDeliverySerializer(serializers.ModelSerializer):
    """ Serializer for delivery instances - serializes only non-sensitive data """
    item = ItemSerializer()
    pickup_place = PlaceSerializer()
    delivery_place = PlaceSerializer()

    class Meta:
        model = Delivery
        fields = ['safe_id', 'created_at', 'item', 'pickup_place', 'delivery_place',
                  'state', 'expected_duration', 'route_distance', 'price']
        read_only_fields = ['safe_id', 'created_at', 'state', 'expected_duration', 'route_distance', 'price']

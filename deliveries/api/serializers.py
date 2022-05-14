from django.contrib.gis.geos import Point
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import Person, Account
from deliveries.models import Item, Delivery, Place
from accounts.api.serializers import PersonSerializer, AccountSerializer
from django.db.utils import IntegrityError


class ItemSerializer(serializers.ModelSerializer):
    """ Serializer for item instances """
    description = serializers.CharField(required=False)

    class Meta:
        model = Item
        fields = ['name', 'description', 'photo', 'size', 'weight', 'fragile']


class PlaceSerializer(serializers.ModelSerializer):
    """
    Model serializer for Place instances.
    """
    place_id = serializers.CharField(max_length=2000)
    latitude = serializers.FloatField(max_value=90., min_value=-90., write_only=True)
    longitude = serializers.FloatField(max_value=180., min_value=-180., write_only=True)

    def to_representation(self, obj):
        """
        Serializes a POINT coordinate structure into a more readable latitude and longitude pair.

        :param obj: Place object being serialized
        :return: JSON representation of the place object.
        """
        representation = super().to_representation(obj)
        point = obj.coordinates
        representation['latitude'] = point.coords[1]
        representation['longitude'] = point.coords[0]
        return representation

    class Meta:
        model = Place
        fields = ['place_id', 'formatted_address', 'country', 'city',
                  'street_address', 'postal_code', 'latitude', 'longitude']

    def create(self, validated_data):
        """
        Create a new place object and save it to database.

        :param validated_data: Place data after validation
        :return: Created Place model instance.
        """
        lat = validated_data.pop('latitude')
        lon = validated_data.pop('longitude')
        place = Place.objects.create(
            **validated_data,
            coordinates=Point(lon, lat, srid=4236)
        )
        return place


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
        try:
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
        except IntegrityError as exc:
            start = exc.__str__().find('DETAIL')+8
            end = exc.__str__().find('.', start)+1
            raise ValidationError({'detail': exc.__str__()[start:end]})

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

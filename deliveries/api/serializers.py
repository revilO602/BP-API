from django.contrib.gis.geos import Point
from rest_framework import serializers
from accounts.models import Person, Account
from deliveries.models import Item, Delivery
from places.models import Place
from accounts.api.serializers import PersonSerializer, AccountSerializer
from places.api.serializers import PlaceSerializer


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'description', 'photo', 'size', 'weight', 'fragile']


class DeliverySerializer(serializers.ModelSerializer):
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
                  'courier', 'state']

    # refaktoring extrakcie koordinatov - dost mozno aj nepytat POINT na API urovni ale vybudovat ho z lon a lat
    def create(self, validated_data):
        pickup_place_data = validated_data.pop('pickup_place')
        delivery_place_data = validated_data.pop('delivery_place')
        receiver_data = validated_data.pop('receiver')
        pickup_place_coordinates = Point(pickup_place_data.pop('longitude'), pickup_place_data.pop('latitude'))
        delivery_place_coordinates = Point(delivery_place_data.pop('longitude'), delivery_place_data.pop('latitude'))
        delivery = Delivery.objects.create(
            item=Item.objects.create(**validated_data.pop('item')),
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
    item = ItemSerializer()
    pickup_place = PlaceSerializer()
    delivery_place = PlaceSerializer()

    class Meta:
        model = Delivery
        fields = ['safe_id', 'created_at', 'item', 'pickup_place', 'delivery_place', 'state']

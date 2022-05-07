from rest_framework import serializers
from places.models import Place, Route
from django.contrib.gis.geos import Point


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


class RouteSerializer(serializers.ModelSerializer):
    """
    Model serializer for Route instances.
    """
    start_address = serializers.CharField(source="delivery.pickup_place.formatted_address")
    destination_address = serializers.CharField(source="delivery.delivery_place.formatted_address")

    class Meta:
        model = Route
        fields = ['id', 'steps', 'polyline', 'start_address', 'destination_address', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'start_address', 'destination_address']

from rest_framework import serializers
from places.models import Place
from django.contrib.gis.geos import Point


class PlaceSerializer(serializers.ModelSerializer):
    place_id = serializers.CharField(max_length=2000)
    latitude = serializers.FloatField(max_value=90., min_value=-90., write_only=True)
    longitude = serializers.FloatField(max_value=180., min_value=-180., write_only=True)

    def to_representation(self, obj):
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
        lat = validated_data.pop('latitude')
        lon = validated_data.pop('longitude')
        place = Place.objects.create(
            **validated_data,
            coordinates=Point(lon, lat, srid=4236)
        )
        return place


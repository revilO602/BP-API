from drf_writable_nested import UniqueFieldsMixin
from rest_framework import serializers
from places.models import Place


class PlaceSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Place
        geo_field = 'coordinates'
        fields = ['place_id', 'formatted_address', 'country', 'city', 'street_address', 'postal_code', 'coordinates']



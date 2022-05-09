from rest_framework import serializers
from routes.models import Route


class RouteSerializer(serializers.ModelSerializer):
    """
    Model serializer for Route instances.
    """
    start_address = serializers.CharField(source="delivery.pickup_place.formatted_address", read_only=True)
    destination_address = serializers.CharField(source="delivery.delivery_place.formatted_address", read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'steps', 'polyline', 'start_address', 'destination_address', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'start_address', 'destination_address']

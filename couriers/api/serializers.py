from rest_framework import serializers

from couriers.models import Courier


class CourierSerializer(serializers.ModelSerializer):
    """
    Serializer for courier instances.
    * All personal data is write only.
    """
    class Meta:
        model = Courier
        fields = ['id_number', 'id_expiration_date', 'dl_number',
                  'dl_expiration_date', 'vehicle_type', 'home_address']
        extra_kwargs = {
            'id_number': {'write_only': True},
            'id_expiration_date': {'write_only': True},
            'dl_number': {'write_only': True},
            'dl_expiration_date': {'write_only': True},
            'home_address': {'write_only': True},
        }


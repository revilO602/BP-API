from helpers.models import TrackingModule
from django.contrib.gis.db import models




# # class Coordinates(TrackingModule):
# #     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#
#
#
#     def __str__(self):
#         return '{}'.format(self.created_at)


class Place(TrackingModule):
    place_id = models.CharField(max_length=2000, primary_key=True)
    formatted_address = models.CharField(max_length=2000)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    street_address = models.CharField(max_length=500)
    postal_code = models.CharField(max_length=255)
    coordinates = models.PointField(geography=True, srid=4326)

    def __str__(self):
        return '{}'.format(self.formatted_address)

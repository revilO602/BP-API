from helpers.models import TrackingModel
from django.contrib.gis.db import models


class Place(TrackingModel):
    place_id = models.CharField(max_length=2000, primary_key=True)
    formatted_address = models.CharField(max_length=2000)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    street_address = models.CharField(max_length=500)
    postal_code = models.CharField(max_length=255)
    coordinates = models.PointField(geography=True, srid=4326)

    class Meta:
        db_table = "place"

    def __str__(self):
        return self.formatted_address

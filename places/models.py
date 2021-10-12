from django.db import models
from helpers.models import TrackingModule
import uuid
from account.models import Person


# class Coordinates(TrackingModule):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     latitude
#     longitude
#
#
#     def __str__(self):
#         return '{}'.format(self.created_at)
#
#
# class Place(TrackingModule):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     country = models.CharField(max_length=255)
#     city = models.CharField(max_length=255)
#     street = models.CharField(max_length=255)
#     street_number = models.CharField(max_length=255)
#     postal_code = models.CharField(max_length=255)
#
#     def __str__(self):
#         return '{} {}, {} {}, {}'.format(self.street, self.street_number, self.postal_code, self.city, self.country)


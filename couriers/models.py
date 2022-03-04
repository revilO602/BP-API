from django.contrib.gis.db import models

from account.models import Account, Person
from helpers.models import TrackingModule
from places.models import Place
import uuid


def upload_courier_picture(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return 'courier_pictures/{filename}'.format(filename=filename)


class Courier(TrackingModule):
    class SizeType(models.TextChoices):
        SMALL = 'small'
        MEDIUM = 'medium'
        LARGE = 'large'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_photo_front = models.ImageField(upload_to=upload_courier_picture, blank=True, null=True)
    id_photo_back = models.ImageField(upload_to=upload_courier_picture, blank=True, null=True)
    dl_photo_front = models.ImageField(upload_to=upload_courier_picture, blank=True, null=True)
    dl_photo_back = models.ImageField(upload_to=upload_courier_picture, blank=True, null=True)
    vehicle_type = models.CharField(max_length=6, choices=SizeType.choices, default=SizeType.MEDIUM)
    home_address = models.CharField(max_length=2000, default='')
    coordinates = models.PointField(geography=True, srid=4326, default='POINT(0.0 0.0)')
    user = models.OneToOneField(Account, on_delete=models.RESTRICT, blank=True, null=True)
    person = models.OneToOneField(Person, on_delete=models.RESTRICT, blank=True, null=True, default=None)

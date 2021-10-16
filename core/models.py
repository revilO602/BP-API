from django.db import models
from helpers.models import TrackingModule
import uuid
from account.models import Person
from places.models import Place


def upload_item_picture(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return 'item_pictures/{filename}'.format(filename=filename)


class Item(TrackingModule):
    class SizeType(models.TextChoices):
        SMALL = 'small'
        MEDIUM = 'medium'
        LARGE = 'large'

    class WeightType(models.TextChoices):
        LIGHT = 'light'
        MEDIUM = 'medium'
        HEAVY = 'heavy'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to=upload_item_picture, blank=True, null=True)
    size = models.CharField(max_length=6, choices=SizeType.choices, default=SizeType.MEDIUM)
    weight = models.CharField(max_length=6, choices=WeightType.choices, default=WeightType.MEDIUM)
    fragile = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.name)


class Delivery(TrackingModule):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(Person, on_delete=models.RESTRICT, null=True, related_name='sender')
    receiver = models.ForeignKey(Person, on_delete=models.RESTRICT, null=True, related_name='receiver')
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, null=True)
    pickup_place = models.ForeignKey(Place, on_delete=models.RESTRICT, related_name='pickup_place')
    delivery_place = models.ForeignKey(Place, on_delete=models.RESTRICT, related_name='delivery_place')
    #courier

    def __str__(self):
        return '{}'.format(self.created_at)

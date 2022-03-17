import uuid
from django.db import models

from helpers.models import TrackingModel
from accounts.models import Person, Account
from places.models import Place
from helpers.enums import (SizeType, WeightType, DeliveryState)


def upload_item_picture(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return 'item_pictures/{filename}'.format(filename=filename)


class Item(TrackingModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to=upload_item_picture, blank=True, null=True)
    size = models.CharField(max_length=6, choices=SizeType.choices, default=SizeType.MEDIUM)
    weight = models.CharField(max_length=6, choices=WeightType.choices, default=WeightType.MEDIUM)
    fragile = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        db_table = "item"


class Delivery(TrackingModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(Person, on_delete=models.RESTRICT, null=True, related_name='sender')
    receiver_account = models.ForeignKey(Account, on_delete=models.RESTRICT, null=True, related_name='receiver_account')
    receiver = models.ForeignKey(Person, on_delete=models.RESTRICT, null=True, related_name='receiver')
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, null=True)
    pickup_place = models.ForeignKey(Place, on_delete=models.RESTRICT, related_name='pickup_place', blank=True,
                                     null=True)
    delivery_place = models.ForeignKey(Place, on_delete=models.RESTRICT, related_name='delivery_place', blank=True,
                                       null=True)
    courier = models.ForeignKey(Account, on_delete=models.RESTRICT, blank=True, null=True, default=None)
    state = models.CharField(max_length=13, choices=DeliveryState.choices, default=DeliveryState.READY)
    safe_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        db_table = "delivery"

    def __str__(self):
        return '{}'.format(self.created_at)

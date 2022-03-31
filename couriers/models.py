from django.contrib.gis.db import models

from helpers.models import TrackingModel
from helpers.enums import SizeType
import uuid


class Courier(TrackingModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_number = models.CharField(max_length=20)
    id_expiration_date = models.DateField(default='2022-03-20')
    dl_number = models.CharField(max_length=20)
    dl_expiration_date = models.DateField(default='2022-03-20')
    vehicle_type = models.CharField(max_length=6, choices=SizeType.choices, default=SizeType.MEDIUM)
    home_address = models.CharField(max_length=2000)

    class Meta:
        db_table = "courier"

import uuid
from deliveries.models import Delivery
from helpers.models import TrackingModel
from django.db import models


class Route(TrackingModel):
    """ Model for route data """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.ForeignKey(Delivery, on_delete=models.SET_NULL, null=True, related_name='delivery')
    polyline = models.CharField(max_length=2000)
    steps = models.JSONField()

    class Meta:
        db_table = "route"

    def __str__(self):
        return self.created_at

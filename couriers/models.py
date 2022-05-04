from django.contrib.gis.db import models
import pgcrypto
from helpers.models import TrackingModel
from helpers.enums import SizeType
import uuid


class Courier(TrackingModel):
    """
    Courier model responsible for holding data required for being a courier.
    * All personal data is encrypted on the database level.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_number = pgcrypto.EncryptedCharField(models.CharField(max_length=20))
    id_expiration_date = pgcrypto.EncryptedDateField(models.DateField())
    dl_number = pgcrypto.EncryptedCharField(models.CharField(max_length=20))
    dl_expiration_date = pgcrypto.EncryptedDateField(models.DateField())
    vehicle_type = models.CharField(max_length=6, choices=SizeType.choices, default=SizeType.MEDIUM)
    home_address = pgcrypto.EncryptedCharField(models.CharField(max_length=2000))

    class Meta:
        db_table = "courier"

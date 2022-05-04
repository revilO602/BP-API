from django.db import models


class SizeType(models.TextChoices):
    """
    Size categories used throughout the app.
    """
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'


class WeightType(models.TextChoices):
    """
    Weight categories used throughout the app.
    """
    LIGHT = 'light'
    MEDIUM = 'medium'
    HEAVY = 'heavy'


class DeliveryState(models.TextChoices):
    """
    Enumeration of possible delivery states.

    ready - delivery is ready to be assigned to courier
    assigned - courier is picking up delivery
    delivering - delivery is being delivered by courier
    delivered - delivery has been delivered
    undeliverable - delivery cant be delivered
    """
    READY = 'ready'
    ASSIGNED = 'assigned'
    DELIVERING = 'delivering'
    DELIVERED = 'delivered'
    UNDELIVERABLE = 'undeliverable'

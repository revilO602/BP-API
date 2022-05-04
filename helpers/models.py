from django.db import models


class TrackingModel(models.Model):
    """
    Abstract model that provides all tracking fields to models that inherit from it.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)

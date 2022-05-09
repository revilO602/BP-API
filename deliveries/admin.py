from django.contrib.gis import admin
from deliveries.models import Delivery, Item, Place

admin.site.register(Delivery)
admin.site.register(Item)
admin.site.register(Place, admin.OSMGeoAdmin)

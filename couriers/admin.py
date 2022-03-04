from django.contrib.gis import admin
from couriers.models import Courier


admin.site.register(Courier, admin.OSMGeoAdmin)


from django.db import models

# Create your models here.
from django.contrib.gis.db import models


class NASbox(models.Model):
    name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    capacity = models.IntegerField()
    location = models.PointField(geography=True, srid=4326)

    def __str__(self):
        return self.name


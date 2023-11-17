from django.db import models
from django.contrib.gis.db import models as gisModels

# Create your models here.
class BCGS20k(models.Model):

    tile_20k = models.CharField(max_length=32, blank=True, primary_key=True)
    geometry = gisModels.MultiPolygonField(geography=True, blank=True, null=True)
    priority = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bcgs20k'
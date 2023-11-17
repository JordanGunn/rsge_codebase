from django.db import models
from django.contrib.gis.db import models as gisModels

# Create your models here.
class BCGS2500k(models.Model):

    tile_2500k = models.CharField(max_length=32, blank=True, primary_key=True)
    geometry = gisModels.MultiPolygonField(geography=True, blank=True, null=True)
    tile_20k = models.ForeignKey('BCGS20k.BCGS20k', models.DO_NOTHING, blank=True, null=True)
    lidar_id = models.ForeignKey('LidarClassified.LidarClassified', models.DO_NOTHING, blank=True, null=True)
    epsg_code = models.ForeignKey('SpatialReference.SpatialReference', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bcgs2500k'
from django.db import models
from django.contrib.gis.db import models as gisModels

# Create your models here.
class LidarClassified(models.Model):

    id = models.OneToOneField('Lidar.Lidar', on_delete=models.CASCADE, primary_key=True)
    bounding_box = gisModels.PolygonField(blank=True, null=True)
    tile_2500k = models.ForeignKey('BCGS2500k.BCGS2500k', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lidarclassified'
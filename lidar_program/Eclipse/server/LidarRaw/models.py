from django.db import models
from django.contrib.gis.db import models as gisModels

# Create your models here.
class LidarRaw(models.Model):

    id = models.OneToOneField('Lidar.Lidar', on_delete=models.CASCADE, primary_key=True)
    convex_hull = gisModels.PolygonField(blank=True, null=True)
    file_source_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lidarraw'
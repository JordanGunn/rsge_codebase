from django.db import models

# Create your models here.
class SpatialReference(models.Model):

    epsg_code = models.IntegerField(primary_key=True)
    proj_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'spatialreference'
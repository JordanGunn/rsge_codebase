from django.db import models

# Create your models here.
class Epoch(models.Model):

    id = models.AutoField(primary_key=True)
    epoch_year = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    epsg_code = models.ForeignKey('SpatialReference.SpatialReference', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'epoch'
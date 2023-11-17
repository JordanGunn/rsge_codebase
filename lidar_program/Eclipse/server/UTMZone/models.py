from django.db import models

# Create your models here.
class UTMZone(models.Model):

    zone_number = models.IntegerField(primary_key=True)
    delivery = models.ForeignKey('SpatialReference.SpatialReference', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'utmzone'
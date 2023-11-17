from django.db import models
from django.contrib.gis.db import models as gisModels

# Create your models here.
class DerivedProduct(models.Model):

    class ProductType(models.TextChoices):
        DEM = 'DEM'
        DSM = 'DSM'
        CHM = 'CHM'

    id = models.AutoField(primary_key=True)
    derived_product_type = models.CharField(choices=ProductType.choices)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.CharField(max_length=255, blank=True, null=True)
    x_min = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    x_max = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    y_min = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    y_max = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    bounding_box = gisModels.PolygonField(blank=True, null=True)
    epsg_code = models.ForeignKey('SpatialReference.SpatialReference', models.DO_NOTHING, blank=True, null=True)
    nas = models.ForeignKey('NASBox.NASBox', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'derivedproduct'
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models


class Bcgs20K(models.Model):
    tile_20k = models.CharField(primary_key=True, max_length=32)
    geom = models.MultiPolygonField(srid=0, blank=True, null=True)
    priority = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bcgs20k'


class Bcgs2500K(models.Model):
    tile_2500k = models.CharField(primary_key=True, max_length=32)
    geom = models.MultiPolygonField(srid=0, blank=True, null=True)
    lidar = models.ForeignKey('Lidarclassified', models.DO_NOTHING, blank=True, null=True)
    tile_20k = models.ForeignKey(Bcgs20K, models.DO_NOTHING, db_column='tile_20k')

    class Meta:
        managed = False
        db_table = 'bcgs2500k'


class Controlpoint(models.Model):

    point_name = models.CharField(max_length=255, blank=True, null=True)
    point_geometry = models.TextField(blank=True, null=True)  # This field type is a guess.
    delivery = models.ForeignKey('Delivery', models.DO_NOTHING, blank=True, null=True)
    epsg_code = models.ForeignKey('Spatialreference', models.DO_NOTHING, db_column='epsg_code', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'controlpoint'


class Delivery(models.Model):  # DONE

    receiver_name = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    nas = models.ForeignKey('Nasbox', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'delivery'


class Derivedproduct(models.Model):
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.CharField(max_length=255, blank=True, null=True)
    x_min = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    x_max = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    y_min = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    y_max = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    bounding_box = models.TextField(blank=True, null=True)  # This field type is a guess.
    epsg_code = models.IntegerField(blank=True, null=True)
    derived_product = models.TextField(blank=True, null=True)  # This field type is a guess.
    nas = models.ForeignKey('Nasbox', models.DO_NOTHING, blank=True, null=True)
    tile_20k = models.ForeignKey(Bcgs20K, models.DO_NOTHING, db_column='tile_20k', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'derivedproduct'


class Drive(models.Model):  # DONE
    serial_number = models.CharField(max_length=255)
    storage_total_gb = models.DecimalField(max_digits=4, decimal_places=2)
    storage_used_gb = models.DecimalField(max_digits=4, decimal_places=2)
    file_count = models.IntegerField(blank=True, null=True)
    nas = models.ForeignKey('Nasbox', models.DO_NOTHING, blank=True, null=True)
    delivery = models.ForeignKey(Delivery, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'drive'


class Epoch(models.Model):
    epoch_year = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    epsg_code = models.ForeignKey('Spatialreference', models.DO_NOTHING, db_column='epsg_code', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'epoch'


class Lidar(models.Model):  # DONE
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.CharField(max_length=255, blank=True, null=True)
    x_min = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    x_max = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    y_min = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    y_max = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    point_record_format = models.IntegerField(blank=True, null=True)
    epsg_code = models.IntegerField(blank=True, null=True)
    version = models.FloatField(blank=True, null=True)
    lidar_type = models.CharField(max_length=1, blank=True, null=True)
    nas = models.ForeignKey('Nasbox', models.DO_NOTHING, blank=True, null=True)
    delivery = models.ForeignKey(Delivery, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lidar'


class Lidarclassified(models.Model):
    id = models.OneToOneField(Lidar, models.DO_NOTHING, db_column='id', primary_key=True)
    bounding_box = models.TextField(blank=True, null=True)  # This field type is a guess.
    tile_2500k = models.ForeignKey(Bcgs2500K, models.DO_NOTHING, db_column='tile_2500k', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lidarclassified'


class Lidarraw(models.Model):
    id = models.OneToOneField(Lidar, models.DO_NOTHING, db_column='id', primary_key=True)
    convex_hull = models.TextField(blank=True, null=True)  # This field type is a guess.
    file_source_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lidarraw'


class Nasbox(models.Model):  # DONE
    name = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    ipv4_addr = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'nasbox'


class Processingstatus(models.Model):
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    lidar = models.ForeignKey(Lidar, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'processingstatus'


class Spatialreference(models.Model):
    epsg_code = models.IntegerField(primary_key=True)
    sr_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'spatialreference'


class Utmzone(models.Model):
    zone_number = models.IntegerField(primary_key=True)
    epsg_code = models.ForeignKey(Spatialreference, models.DO_NOTHING, db_column='epsg_code', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'utmzone'

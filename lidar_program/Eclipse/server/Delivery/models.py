from django.contrib.gis.db import models


# Create your models here.
class Delivery(models.Model):

    id = models.AutoField(primary_key=True)
    receiver_name = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    nas = models.ForeignKey('NASBox.NASBox', models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return f"Delivery {self.id}: {self.timestamp}"

    class Meta:
        managed = False
        db_table = 'delivery'

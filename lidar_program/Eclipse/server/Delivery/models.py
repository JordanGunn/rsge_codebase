from django.contrib.gis.db import models
from datetime import datetime


# Create your models here.
class Delivery(models.Model):

    id = models.AutoField(primary_key=True)
    receiver_name = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.now, blank=True, null=True)

    def __str__(self):
        return f"Delivery {self.id}: {self.timestamp}"

    class Meta:
        managed = False
        db_table = 'delivery'

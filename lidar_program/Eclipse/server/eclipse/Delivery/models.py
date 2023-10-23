from django.contrib.gis.db import models


# Create your models here.
class Delivery(models.Model):

    delivery_id = models.AutoField(primary_key=True)
    coverage = models.MultiPolygonField(srid=3153)  # using Albers Conic Projection (CSRS)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery {self.delivery_id}: {self.timestamp}"


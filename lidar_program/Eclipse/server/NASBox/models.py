from django.db import models

# Create your models here.
from django.contrib.gis.db import models


class NASBox(models.Model):
    nas_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    ipv4_addr = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.name}: {self.ipv4_addr}"


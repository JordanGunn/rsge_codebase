from django.contrib.gis.db import models


class NASBox(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    ipv4_addr = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name}: {self.ipv4_addr}"

    class Meta:
        managed = False
        db_table = 'nasbox'

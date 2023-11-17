from django.db import models
from datetime import datetime

class ProcessingStatus(models.Model):

    class Status(models.TextChoices):
        RAW = 'Raw'
        ADJUSTED = 'Adjusted'
        CLASSIFIED = 'Classified'
        QUALITYCONTROLLED = 'QualityControlled'
        ACCEPTED = 'Accepted'
        REJECTED = 'Rejected'
    
    id = models.AutoField(primary_key=True)
    status = models.CharField(choices=Status.choices)
    timestamp = models.DateTimeField(default=datetime.now, blank=True, null=True)
    processed_by = models.CharField(max_length=255, blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    lidar_id = models.ForeignKey('Lidar.Lidar', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'processingstatus'
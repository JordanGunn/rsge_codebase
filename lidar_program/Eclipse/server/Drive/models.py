# Create your models here.
from django.db import models


class Drive(models.Model):
    serial_number = models.CharField(max_length=255)
    receiver_name = models.CharField(max_length=255)
    storage_total_gb = models.DecimalField(max_digits=4, decimal_places=2)
    storage_used_gb = models.DecimalField(max_digits=4, decimal_places=2)
    file_count = models.IntegerField()
    nas_id = models.ForeignKey('NASBox.NASBoxModel', on_delete=models.CASCADE)
    delivery_id = models.ForeignKey('Delivery.DeliveryModel', on_delete=models.CASCADE)
    # Add other fields as needed


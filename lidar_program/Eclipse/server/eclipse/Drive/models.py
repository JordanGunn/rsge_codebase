# Create your models here.
from django.db import models


class Drive(models.Model):
    serial_number = models.CharField(max_length=100)
    receiver_name = models.CharField(max_length=100)
    date_received = models.DateTimeField()
    nas_id = models.ForeignKey('NASbox.NASBoxModel', on_delete=models.CASCADE)
    delivery_id = models.ForeignKey('Delivery.DeliveryModel', on_delete=models.CASCADE)
    # Add other fields as needed


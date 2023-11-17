from rest_framework import serializers
from .models import Lidar

class LidarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lidar
        fields = '__all__'
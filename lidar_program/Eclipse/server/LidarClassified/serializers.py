from rest_framework import serializers
from .models import LidarClassified

class LidarClassifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = LidarClassified
        fields = '__all__'
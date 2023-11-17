from rest_framework import serializers
from .models import LidarRaw

class LidarRawSerializer(serializers.ModelSerializer):
    class Meta:
        model = LidarRaw
        fields = '__all__'
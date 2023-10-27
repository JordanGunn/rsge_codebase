from rest_framework import serializers
from .models import Drive


class DriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drive
        fields = '__all__'

from rest_framework import serializers
from .models import UTMZone

class UTMZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = UTMZone
        fields = '__all__'
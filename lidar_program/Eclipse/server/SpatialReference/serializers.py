from rest_framework import serializers
from .models import SpatialReference

class SpatialReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpatialReference
        fields = '__all__'
from rest_framework import serializers
from .models import NASBox

class NASboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = NASBox
        fields = '__all__'

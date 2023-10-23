from rest_framework import serializers
from .models import NASbox

class NASboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = NASbox
        fields = '__all__'

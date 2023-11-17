from rest_framework import serializers
from .models import Epoch

class EpochSerializer(serializers.ModelSerializer):
    class Meta:
        model = Epoch
        fields = '__all__'
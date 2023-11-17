from rest_framework import serializers
from .models import ProcessingStatus

class ProcessingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingStatus
        fields = '__all__'
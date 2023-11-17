from rest_framework import serializers
from .models import BCGS20k

class BCGS20kSerializer(serializers.ModelSerializer):
    class Meta:
        model = BCGS20k
        fields = '__all__'
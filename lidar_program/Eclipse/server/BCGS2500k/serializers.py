from rest_framework import serializers
from .models import BCGS2500k

class BCGS2500kSerializer(serializers.ModelSerializer):
    class Meta:
        model = BCGS2500k
        fields = '__all__'
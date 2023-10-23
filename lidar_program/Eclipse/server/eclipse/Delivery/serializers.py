# Delivery/serializers.py
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Delivery


class DeliverySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Delivery
        geo_field = 'coverage'
        fields = '__all__'

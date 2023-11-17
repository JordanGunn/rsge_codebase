from rest_framework import serializers
from .models import DerivedProduct

class DerivedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DerivedProduct
        fields = '__all__'
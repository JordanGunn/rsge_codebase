# Create your views here.
from rest_framework import viewsets
from .models import LidarClassified
from .serializers import LidarClassified

class LidarClassifiedViewSet(viewsets.ModelViewSet):
    queryset = LidarClassified.objects.all()
    serializer_class = LidarClassified
# Create your views here.
from rest_framework import viewsets
from .models import LidarRaw
from .serializers import LidarRaw

class LidarRawViewSet(viewsets.ModelViewSet):
    queryset = LidarRaw.objects.all()
    serializer_class = LidarRaw
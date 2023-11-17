# Create your views here.
from rest_framework import viewsets
from .models import UTMZone
from .serializers import UTMZone

class UTMZoneViewSet(viewsets.ModelViewSet):
    queryset = UTMZone.objects.all()
    serializer_class = UTMZone
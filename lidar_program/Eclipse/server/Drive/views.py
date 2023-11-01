# Create your views here.
from rest_framework import viewsets
from .models import Drive
from .serializers import DriveSerializer


class DriveViewSet(viewsets.ModelViewSet):
    queryset = Drive.objects.all()
    serializer_class = DriveSerializer

from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Drive
from .serializers import DriveSerializer

class NASboxViewSet(viewsets.ModelViewSet):
    queryset = Drive.objects.all()
    serializer_class = DriveSerializer

from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import NASbox
from .serializers import NASboxSerializer

class NASboxViewSet(viewsets.ModelViewSet):
    queryset = NASbox.objects.all()
    serializer_class = NASboxSerializer

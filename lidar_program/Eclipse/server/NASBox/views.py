from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import NASBox
from .serializers import NASboxSerializer

class NASboxViewSet(viewsets.ModelViewSet):
    queryset = NASBox.objects.all()
    serializer_class = NASboxSerializer

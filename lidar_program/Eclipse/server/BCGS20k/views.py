# Create your views here.
from rest_framework import viewsets
from .models import BCGS20k
from .serializers import BCGS20k

class BCGS20kViewSet(viewsets.ModelViewSet):
    queryset = BCGS20k.objects.all()
    serializer_class = BCGS20k
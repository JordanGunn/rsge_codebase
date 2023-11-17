# Create your views here.
from rest_framework import viewsets
from .models import BCGS2500k
from .serializers import BCGS2500k

class BCGS2500kViewSet(viewsets.ModelViewSet):
    queryset = BCGS2500k.objects.all()
    serializer_class = BCGS2500k
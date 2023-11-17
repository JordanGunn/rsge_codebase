"""
URL configuration for eclipse project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# django imports
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# eclipse imports
from Drive.views import DriveViewSet
from NASBox.views import NASboxViewSet
from Delivery.views import DeliveryViewSet
from Lidar.views import LidarViewSet
from ProcessingStatus.views import ProcessingStatusViewSet
from LidarClassified.views import LidarClassifiedViewSet
from LidarRaw.views import LidarRawViewSet
from BCGS2500k.views import BCGS2500kViewSet
from BCGS20k.views import BCGS20kViewSet
from SpatialReference.views import SpatialReferenceViewSet
from UTMZone.views import UTMZoneViewSet
from Epoch.views import EpochViewSet
from DerivedProduct.views import DerivedProductViewSet

# router registration for endpoints
router = DefaultRouter()
router.register(r'drive', DriveViewSet)
router.register(r'nasbox', NASboxViewSet)
router.register(r'delivery', DeliveryViewSet)
router.register(r'lidar', LidarViewSet)
router.register(r'processingstatus', ProcessingStatusViewSet)
router.register(r'lidarclassified', LidarClassifiedViewSet)
router.register(r'lidarraw', LidarRawViewSet)
router.register(r'bcgs2500k', BCGS2500kViewSet)
router.register(r'bcgs20k', BCGS20kViewSet)
router.register(r'spatialreference', SpatialReferenceViewSet)
router.register(r'utmzone', UTMZoneViewSet)
router.register(r'epoch', EpochViewSet)
router.register(r'derivedproduct', DerivedProductViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

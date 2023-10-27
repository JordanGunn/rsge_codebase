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
from NASbox.views import NASboxViewSet
from Delivery.views import DeliveryViewSet

# router registration for endpoints
router = DefaultRouter()
router.register(r'drive', DriveViewSet)
router.register(r'nasbox', NASboxViewSet)
router.register(r'delivery', DeliveryViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

print()

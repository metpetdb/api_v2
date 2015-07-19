"""metpetdb_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

#TODO: Move URLs into their own respective applications.

from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers
from api.samples.v1.views import (
    SampleViewSet,
    MineralViewSet,
    RockTypeViewSet,
    RegionViewSet,
    ReferenceViewSet,
    CollectorViewSet,
    SubsampleViewSet,
)
from api.users.v1.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'samples', SampleViewSet)
router.register(r'subsamples', SubsampleViewSet)
router.register(r'minerals', MineralViewSet)
router.register(r'rock_types', RockTypeViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'references', ReferenceViewSet)
router.register(r'collectors', CollectorViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
]

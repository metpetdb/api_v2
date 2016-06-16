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


from api.chemical_analyses.v1.views import (
    ChemicalAnalysisViewSet,
    ElementViewSet,
    OxideViewSet,
)
from api.samples.v1.views import (
    SampleViewSet,
    MineralViewSet,
    RockTypeViewSet,
    RegionViewSet,
    ReferenceViewSet,
    CollectorViewSet,
    SubsampleViewSet,
    MetamorphicRegionViewSet,
    MetamorphicGradeViewSet,
    GeoReferenceViewSet,
    SubsampleTypeViewSet,
    SampleNumbersView,
    CountryNamesView,
    SampleOwnerNamesView,
)
from api.users.v1.views import UserViewSet

from api.bulk_upload.v1.views import BulkUploadViewSet


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'samples', SampleViewSet)
router.register(r'subsamples', SubsampleViewSet)
router.register(r'subsample_types', SubsampleTypeViewSet)
router.register(r'chemical_analyses', ChemicalAnalysisViewSet)
router.register(r'metamorphic_regions', MetamorphicRegionViewSet)
router.register(r'metamorphic_grades', MetamorphicGradeViewSet)
router.register(r'minerals', MineralViewSet)
router.register(r'elements', ElementViewSet)
router.register(r'oxides', OxideViewSet)
router.register(r'georeferences', GeoReferenceViewSet)
router.register(r'rock_types', RockTypeViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'references', ReferenceViewSet)
router.register(r'collectors', CollectorViewSet)
router.register(r'bulk_upload', BulkUploadViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api/admin/', include(admin.site.urls)),
    url(r'^api/auth/', include('djoser.urls.authtoken')),

    url(r'^api/sample_numbers/$', SampleNumbersView.as_view()),
    url(r'^api/country_names/$', CountryNamesView.as_view()),
    url(r'^api/sample_owner_names/$', SampleOwnerNamesView.as_view()),
]

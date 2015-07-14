from rest_framework import viewsets

from api.samples.v1.serializers import (
    SampleSerializer,
    RockTypeSerializer,
    MineralSerializer,
    RegionSerializer,
    ReferenceSerializer,
    CollectorSerializer,
    SubsampleSerializer,
)
from apps.samples.models import (
    Sample,
    RockType,
    Mineral,
    Region,
    Reference,
    Collector,
    Subsample,
)


class SampleViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    filter_fields = ('collector_name', 'rock_type__name',)


class SubsampleViewSet(viewsets.ModelViewSet):
    queryset = Subsample.objects.all()
    serializer_class = SubsampleSerializer


class RockTypeViewSet(viewsets.ModelViewSet):
    queryset = RockType.objects.all()
    serializer_class = RockTypeSerializer


class MineralViewSet(viewsets.ModelViewSet):
    queryset = Mineral.objects.all()
    serializer_class = MineralSerializer


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


class CollectorViewSet(viewsets.ModelViewSet):
    queryset = Collector.objects.all()
    serializer_class = CollectorSerializer

from rest_framework import viewsets
from rest_framework.response import Response
from api.lib.query import sample_qs_optimizer

from api.samples.lib.query import sample_query
from api.samples.v1.serializers import (
    SampleSerializer,
    RockTypeSerializer,
    MineralSerializer,
    RegionSerializer,
    ReferenceSerializer,
    CollectorSerializer,
    SubsampleSerializer,
    MetamorphicRegionSerializer,
    MetamorphicGradeSerializer,
)
from apps.samples.models import (
    Sample,
    RockType,
    Mineral,
    Region,
    Reference,
    Collector,
    Subsample,
    MetamorphicRegion,
    MetamorphicGrade,
)


class SampleViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer

    def list(self, request, *args, **kwargs):
        params = request.QUERY_PARAMS
        qs = self.get_queryset().distinct()
        qs = sample_qs_optimizer(params, qs)
        qs = sample_query(params, qs)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


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


class MetamorphicRegionViewSet(viewsets.ModelViewSet):
    queryset = MetamorphicRegion.objects.all()
    serializer_class = MetamorphicRegionSerializer


class MetamorphicGradeViewSet(viewsets.ModelViewSet):
    queryset = MetamorphicGrade.objects.all()
    serializer_class = MetamorphicGradeSerializer

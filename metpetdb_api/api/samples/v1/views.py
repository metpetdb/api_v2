from rest_framework import viewsets
from rest_framework.response import Response

from api.samples.lib.query import sample_query
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

    def list(self, request, *args, **kwargs):
        params = request.QUERY_PARAMS
        qs = self.get_queryset().distinct()

        try:
            fields = params.get('fields').split(',')
            if 'rock_types' in fields:
                qs = qs.select_related('rock_type')
            if 'metamorphic_grades' in fields:
                qs = qs.prefetch_related('metamorphic_grades')
            if 'metamorphic_regions' in fields:
                qs = qs.prefetch_related('metamorphic_regions')
            if 'minerals' in fields:
                qs = qs.prefetch_related('samplemineral_set__mineral')
            if 'owner' in fields:
                qs = qs.prefetch_related('owner')
        except AttributeError:
            qs = qs.select_related('rock_type')
            qs = qs.prefetch_related('metamorphic_grades',
                                     'metamorphic_regions',
                                     'samplemineral_set__mineral',
                                     'owner')

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

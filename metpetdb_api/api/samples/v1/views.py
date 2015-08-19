from rest_framework import viewsets
from rest_framework.response import Response
from api.chemical_analyses.lib.query import chemical_analysis_query
from api.lib.query import sample_qs_optimizer, chemical_analyses_qs_optimizer

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
from apps.chemical_analyses.models import ChemicalAnalysis
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

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'PUT':
            kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        params = request.QUERY_PARAMS

        if params.get('chemical_analyses_filters') == 'True':
            chem_qs = ChemicalAnalysis.objects.all()
            chem_qs = chemical_analyses_qs_optimizer(params, chem_qs)
            chem_ids = (chemical_analysis_query(params, chem_qs)
                        .values_list('id'))
            qs = (Sample
                  .objects
                  .filter(subsamples__chemical_analyses__id__in=chem_ids))
        else:
            qs = self.get_queryset().distinct()
            qs = sample_query(params, qs)

        qs = sample_qs_optimizer(params, qs)

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

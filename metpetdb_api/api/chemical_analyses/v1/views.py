from rest_framework import viewsets
from rest_framework.response import Response

from api.chemical_analyses.lib.query import chemical_analysis_query
from api.chemical_analyses.v1.serializers import (
    ChemicalAnalysisSerializer,
    ElementSerializer,
    OxideSerializer,
)
from api.lib.query import sample_qs_optimizer, chemical_analyses_qs_optimizer
from api.samples.lib.query import sample_query

from apps.chemical_analyses.models import ChemicalAnalysis, Element, Oxide
from apps.samples.models import Sample


class ChemicalAnalysisViewSet(viewsets.ModelViewSet):
    queryset = ChemicalAnalysis.objects.all()
    serializer_class = ChemicalAnalysisSerializer

    def list(self, request, *args, **kwargs):
        params = request.query_params

        if params.get('sample_filters') == 'True':
            sample_qs = Sample.objects.all()
            sample_qs = sample_qs_optimizer(params, sample_qs)
            sample_ids = sample_query(params, sample_qs).values_list('id')
            qs = ChemicalAnalysis.objects.filter(
                subsample__sample_id__in=sample_ids)
        else:
            qs = self.get_queryset().distinct()
            qs = chemical_analysis_query(params, qs)

        qs = chemical_analyses_qs_optimizer(params, qs)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ElementViewSet(viewsets.ModelViewSet):
    queryset = Element.objects.all()
    serializer_class = ElementSerializer


class OxideViewSet(viewsets.ModelViewSet):
    queryset = Oxide.objects.all()
    serializer_class = OxideSerializer

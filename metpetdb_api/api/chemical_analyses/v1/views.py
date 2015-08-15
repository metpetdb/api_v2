from rest_framework import viewsets
from rest_framework.response import Response

from api.chemical_analyses.lib.query import chemical_analysis_query
from api.chemical_analyses.v1.serializers import (
    ChemicalAnalysisSerializer,
    ElementSerializer,
    OxideSerializer,
)
from api.lib.query import sample_qs_optimizer
from api.samples.lib.query import sample_query

from apps.chemical_analyses.models import ChemicalAnalysis, Element, Oxide
from apps.samples.models import Sample


class ChemicalAnalysisViewSet(viewsets.ModelViewSet):
    queryset = ChemicalAnalysis.objects.all()
    serializer_class = ChemicalAnalysisSerializer

    def _optimize_qs(self, params, qs):
        try:
            fields = params.get('fields').split(',')

            for field in ('mineral', 'owner', 'subsample'):
                if field in fields:
                    qs = qs.select_related(field)

            if 'elements' in fields:
                qs = qs.prefetch_related('chemicalanalysiselement_set__element')
            if 'oxides' in fields:
                qs = qs.prefetch_related('chemicalanalysisoxide_set__oxide')
        except AttributeError:
            qs = qs.select_related('mineral', 'owner', 'subsample')
            qs = qs.prefetch_related('chemicalanalysiselement_set__element',
                                     'chemicalanalysisoxide_set__oxide')
        return qs

    def list(self, request, *args, **kwargs):
        params = request.QUERY_PARAMS

        if params.get('sample_filters') == 'True':
            sample_qs = Sample.objects.all()
            sample_qs = sample_qs_optimizer(params, sample_qs)
            sample_ids = sample_query(params, sample_qs).values_list('id')
            qs = ChemicalAnalysis.objects.filter(
                subsample__sample_id__in=sample_ids)
        else:
            qs = self.get_queryset().distinct()
            qs = chemical_analysis_query(params, qs)

        qs = self._optimize_qs(params, qs)

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

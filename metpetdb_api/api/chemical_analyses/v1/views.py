from rest_framework import viewsets
from rest_framework.response import Response

from api.chemical_analyses.lib.query import chemical_analysis_query
from apps.chemical_analyses.models import ChemicalAnalysis
from api.chemical_analyses.v1.serializers import ChemicalAnalysisSerializer


class ChemicalAnalysisViewSet(viewsets.ModelViewSet):
    queryset = ChemicalAnalysis.objects.all()
    serializer_class = ChemicalAnalysisSerializer

    def list(self, request, *args, **kwargs):
        params = request.QUERY_PARAMS
        qs = self.get_queryset().distinct()

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

        qs = chemical_analysis_query(params, qs)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

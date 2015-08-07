from rest_framework import viewsets
from api.chemical_analyses.v1.serializers import ChemicalAnalysisSerializer
from apps.chemical_analyses.models import ChemicalAnalysis


class ChemicalAnalysisViewSet(viewsets.ModelViewSet):
    queryset = ChemicalAnalysis.objects.all()
    serializer_class = ChemicalAnalysisSerializer

from api.lib.serializers import DynamicFieldsModelSerializer
from api.samples.v1.serializers import SubsampleSerializer, MineralSerializer
from api.users.v1.serializers import UserSerializer
from apps.chemical_analyses.models import ChemicalAnalysis, \
    ChemicalAnalysisElement, ChemicalAnalysisOxide


class ChemicalAnalysisElementSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ChemicalAnalysisElement


class ChemicalAnalysisOxideSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ChemicalAnalysisOxide


class ChemicalAnalysisSerializer(DynamicFieldsModelSerializer):
    subsample = SubsampleSerializer(read_only=True)
    mineral = MineralSerializer(read_only=True)
    owner = UserSerializer(read_only=True)
    elements = ChemicalAnalysisElementSerializer(
        many=True,
        source='chemicalanalysiselement_set')
    oxides = ChemicalAnalysisOxideSerializer(
        many=True,
        source='chemicalanalysisoxide_set')

    class Meta:
        model = ChemicalAnalysis
        depth = 1

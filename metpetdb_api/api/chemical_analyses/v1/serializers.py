from rest_framework import serializers

from api.lib.serializers import DynamicFieldsModelSerializer
from api.samples.v1.serializers import MineralSerializer
from api.users.v1.serializers import UserSerializer
from apps.chemical_analyses.models import (
    ChemicalAnalysis,
    ChemicalAnalysisElement,
    ChemicalAnalysisOxide,
)
from apps.chemical_analyses.shared_models import Element, Oxide
from apps.samples.models import Subsample, Mineral
from apps.users.models import User
from api.images.v1.serializers import ImageSerializer

CHEMICAL_ANALYSIS_FIELDS = ('reference_x', 'reference_y', 'stage_x', 'stage_y',
                            'analysis_method', 'where_done', 'analyst',
                            'analysis_date', 'date_precision',
                            'description', 'total', 'spot_id', 'reference')


class ChemicalAnalysisElementSerializer(DynamicFieldsModelSerializer):
    # id = serializers.ReadOnlyField(source='element.id')
    # name = serializers.ReadOnlyField(source='element.name')
    # alternate_name = serializers.ReadOnlyField(source='element.alternate_name')
    symbol = serializers.ReadOnlyField(source='element.symbol')
    # atomic_number = serializers.ReadOnlyField(source='element.atomic_number')
    # weight = serializers.ReadOnlyField(source='element.weight')
    # order_id = serializers.ReadOnlyField(source='element.order_id')

    class Meta:
        model = ChemicalAnalysisElement
        fields = (
            # 'id', 
            # 'name', 
            # 'alternate_name', 
            'symbol', 
            # 'atomic_number',
            # 'weight', 
            # 'order_id', 
            'amount', 
            'precision',
            'precision_type', 
            'measurement_unit', 
            # 'min_amount',
            # 'max_amount'
            )


class ChemicalAnalysisOxideSerializer(DynamicFieldsModelSerializer):
    # id = serializers.ReadOnlyField(source='oxide.id')
    # element_id = serializers.ReadOnlyField(source='oxide.element_id')
    # oxidation_state = serializers.ReadOnlyField(source='oxide.oxidation_state')
    species = serializers.ReadOnlyField(source='oxide.species')
    # weight = serializers.ReadOnlyField(source='oxide.weight')
    # cations_per_oxide = serializers.ReadOnlyField(
        # source='oxide.cations_per_oxide')
    # conversion_factor = serializers.ReadOnlyField(
        # source='oxide.conversion_factor')
    # order_id = serializers.ReadOnlyField(source='oxide.order_id')

    class Meta:
        model = ChemicalAnalysisOxide
        fields = (
            # 'id', 
            # 'element_id', 
            # 'oxidation_state', 
            'species', 
            # 'weight',
            # 'cations_per_oxide', 
            # 'conversion_factor', 
            # 'order_id',
            'amount', 
            'precision', 
            'precision_type', 
            'measurement_unit',
            # 'min_amount', 
            # 'max_amount' 
                  )


class ChemicalAnalysisSerializer(DynamicFieldsModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.name')
    sample = serializers.ReadOnlyField(source='subsample.sample.number')
    subsample = serializers.ReadOnlyField(source='subsample.name')
    subsample_type = serializers.ReadOnlyField(source='subsample.subsample_type.name')
    mineral = serializers.ReadOnlyField(source='mineral.name')
    elements = ChemicalAnalysisElementSerializer(
        many=True,
        source='chemicalanalysiselement_set',
        required=False,
    )
    oxides = ChemicalAnalysisOxideSerializer(
        many=True,
        source='chemicalanalysisoxide_set',
        required=False
    )

    class Meta:
        model = ChemicalAnalysis
        depth = 1

        fields = (
            'owner',
            'sample',
            'subsample',
            'subsample_type',
            'mineral',
            'analysis_method',
            'reference',
            'spot_id',
            'where_done',
            'analysis_date',
            # 'date_precision',
            'analyst',
            'reference_x',
            'reference_y',
            'stage_x', 
            'stage_y',
            'description',
            'elements',
            'oxides',
            'total',
            )

    def is_valid(self, raise_exception=False):
        super().is_valid(raise_exception)

        if self.initial_data.get('owner'):
            self._validated_data.update(
                {'owner': User.objects.get(pk=self.initial_data['owner'])})

        if self.initial_data.get('subsample_id'):
            self._validated_data.update(
                {'subsample': (Subsample
                               .objects
                               .get(pk=self.initial_data['subsample_id']))
                 })

        if self.initial_data.get('mineral_id'):
            self._validated_data.update(
                {'mineral': (Mineral
                             .objects
                             .get(pk=self.initial_data['mineral_id']))
                 })

        return not bool(self._errors)

    def create(self, validated_data):
        if validated_data.get('chemicalanalysiselement_set'):
            del validated_data['chemicalanalysiselement_set']

        if validated_data.get('chemicalanalysisoxide_set'):
            del validated_data['chemicalanalysisoxide_set']

        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr in CHEMICAL_ANALYSIS_FIELDS:
                setattr(instance, attr, value)
        instance.save()

        return instance




class ElementSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Element
        fields = '__all__'


class OxideSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Oxide
        fields = '__all__'

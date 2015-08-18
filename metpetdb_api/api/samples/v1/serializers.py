from rest_framework import serializers

from api.lib.serializers import DynamicFieldsModelSerializer
from api.users.v1.serializers import UserSerializer

from apps.chemical_analyses.models import ChemicalAnalysis
from apps.samples.models import (
    MetamorphicGrade,
    MetamorphicRegion,
    RockType,
    Sample,
    Mineral,
    SampleMineral,
    Region,
    Reference,
    Collector,
    Subsample,
)


class RockTypeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = RockType


class MineralSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Mineral


class SampleMineralSerializer(DynamicFieldsModelSerializer):
    id = serializers.ReadOnlyField(source='mineral.id')
    name = serializers.ReadOnlyField(source='mineral.name')
    real_mineral_id = serializers.ReadOnlyField(
                          source='mineral.real_mineral_id'
                      )
    class Meta:
        model = SampleMineral
        fields = ('id', 'name', 'amount', 'real_mineral_id',)


class SampleSerializer(DynamicFieldsModelSerializer):
    rock_types = RockTypeSerializer(many=True, required=False)
    minerals = SampleMineralSerializer(source='samplemineral_set',
                                       many=True)
    owner = UserSerializer()

    # TODO: figure out if there is a better, more efficient way to do this
    subsample_ids = serializers.SerializerMethodField()
    chemical_analyses_ids = serializers.SerializerMethodField()

    class Meta:
        model = Sample
        depth = 1

    def get_subsample_ids(self, obj):
        return Subsample.objects.filter(sample_id=obj.pk).values_list('id',
                                                                      flat=True)

    def get_chemical_analyses_ids(self, obj):
        subsample_ids = obj.subsamples.values_list('id', flat=True)
        return ChemicalAnalysis.objects.filter(
            subsample_id__in=subsample_ids).values_list('id', flat=True)


class SubsampleSerializer(DynamicFieldsModelSerializer):
    sample = SampleSerializer(read_only=True)
    class Meta:
        model = Subsample


class MetamorphicGradeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = MetamorphicGrade


class MetamorphicRegionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = MetamorphicRegion


class RegionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Region


class ReferenceSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Reference


class CollectorSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Collector

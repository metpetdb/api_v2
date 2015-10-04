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
    SubsampleType,
)
from apps.users.models import User

SAMPLE_FIELDS = ('number', 'aliases', 'collection_date', 'description',
                 'location_name', 'location_coords', 'location_error',
                 'date_precision', 'country', 'regions', 'collector_name',
                 'collector_id', 'sesar_number',)

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
    minerals = SampleMineralSerializer(source='samplemineral_set',
                                       many=True)
    owner = UserSerializer(read_only=True)

    # TODO: figure out if there is a better, more efficient way to do this
    subsample_ids = serializers.SerializerMethodField()
    chemical_analyses_ids = serializers.SerializerMethodField()

    class Meta:
        model = Sample
        depth = 1

    def is_valid(self, raise_exception=False):
        super().is_valid(raise_exception)

        if self.initial_data.get('owner'):
            self._validated_data.update(
                {'owner': User.objects.get(pk=self.initial_data['owner'])})

        if self.initial_data.get('rock_type_id'):
            self._validated_data.update(
                {'rock_type': (RockType
                               .objects
                               .get(pk=self.initial_data['rock_type_id']))
                 }
            )

        return not bool(self._errors)

    def create(self, validated_data):
        if validated_data.get('samplemineral_set'):
            del validated_data['samplemineral_set']

        instance = super().create(validated_data)
        return instance


    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr in SAMPLE_FIELDS:
                setattr(instance, attr, value)
        instance.save()

        return instance

    def get_subsample_ids(self, obj):
        return Subsample.objects.filter(sample_id=obj.pk).values_list('id',
                                                                      flat=True)

    def get_chemical_analyses_ids(self, obj):
        subsample_ids = obj.subsamples.values_list('id', flat=True)
        return ChemicalAnalysis.objects.filter(
            subsample_id__in=subsample_ids).values_list('id', flat=True)


class SubsampleSerializer(DynamicFieldsModelSerializer):
    # sample = SampleSerializer(read_only=True)
    class Meta:
        model = Subsample
        depth = 1


class SubsampleTypeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = SubsampleType
        depth = 1


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
